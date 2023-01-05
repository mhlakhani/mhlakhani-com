{
    "route": "post",
    "title": "Setting up secure personal developer infrastructure for/and side projects using tailscale, drone, gitea, and nginx",
    "date": "2022/06/20",
    "tags": ["tailscale", "gitea", "drone", "nginx", "ci", "side-projects", "infrastructure"],
    "excerpt": "Learn how I manage my side project infrastructure, which also powers this blog!",
    "featured": true
}

As alluded to in a [previous post](/blog/2022/06/software-maintenance-sucks/), I recently completed a major overhaul of my personal developer infrastructure. This post will go into *why* I needed to do that and *how* I managed to improve my productivity while improving the security of my network too.

## The setup

Here's how my workflow looked at a high level:

{{ macros::image(src='/static/img/2022/06/old_infra.png', caption='My old infrastructure setup. Full of sadness') }}

That image is a lot to take in, so let's break it down piece by piece.

### First, the machines

I have a cheap VPS on DigitalOcean (2GB RAM, 2 CPUs), which I use to host most of my things - this includes CI, source control, a few side projects, a monitoring setup, and an nginx reverse proxy (which fronts this site, and all the aforementioned tools). This is great for what I need it to do; CPU utilization is usually between 5-10% and RAM usage hovers around 40% - ironically, most of that is used by the monitoring stack.

At home, I have a beefy desktop running windows 11: it has 32GB RAM and an 8-core i9 11900k. It's great for development and I do all my personal computing on it.

From time to time I also like to access my side projects from my phone; which was quite inconvenient.

### The software

I run a lot of things that poor VPS. Leaving out my own code for now, here's what I run and why:

* [*gitea*](https://gitea.io/en-us/) - this provides a self hosted git solution for all my code. Until this upgrade, I was using [*gogs*](https://gogs.io/); but I ran into issues after upgrading my CI software, and, more importantly, `gitea` supported a few more features I needed (such as the container registry, and reverse proxy authentication).
* [*drone*](https://www.drone.io/) - this is a continuous integration solution that lets me test all my commits in an async manner. It also integrates well with `gitea` so tests can run as soon as I push code.
* [*nsd*](https://en.wikipedia.org/wiki/NSD) - a self hosted DNS solution which lets me easily create subdomains as I please.
* [*reads app*](https://reads.mhlakhani.com/) - one of many sites I host, in particular this is the backend for [Hasnain Reads](https://reads.mhlakhani.com). They are all deployed as docker containers using `docker-compose` and `systemd` on the VPS.
* [*nginx*](https://www.nginx.com/) - a famous reverse proxy which proxies to all the above services.
* [*tailscale*](https://tailscale.com/) - an effortless VPN which I just added in the upgrade.
* [*ansible*](https://www.ansible.com/) - I use this to manage all the services on the host and push out updates.
* [*letsencrypt*](https://letsencrypt.org/) - provides free and easy to use SSL certificates so all the sites I serve are secured.

### The workflow

Back to the workflow, now that we know enough about the machines and software. 

On a day with extra free time, I like to sit down and write some code for one of my projects. Once I'm done writing and testing my code locally, I try to deploy and use it not long after. Here's how that would work:

1. I `git push` my code. This connects over `ssh` to `gitea` and pushes the commit.
2. `gitea` fires off a webhook, telling `drone` there is a new commit (connecting via the nginx reverse proxy).
3. After some time, the `drone runner` executes its periodic polling of the server and sees there's a new commit. Then...
4. The runner does a `git pull` for the repo over https (via `nginx`).
5. The runner builds the code.
6. The runner tests the code.
7. The runner does a `docker build` to build a production image on the VPS should I choose to deploy it later.
8. All this time, I'm periodically refreshing the builds page on `drone` to see how long is left. 
9. The build eventually completes, and I use `ansible` to tag the newly built image as `latest` and deploy it on the server.
10. I then connect to the admin UI for my side project, where I have to reauthenticate (either via username/password or Facebook login) every time I use it.
11. I can then use my app as I wish.

This isn't great! As you might have already seen, there are a number of annoyances with this setup:

* The builds are happening on the VPS! For large rust compilations, this can be &gt;30 minutes which is frustrating. It would also run out of memory at times (which is why I upgraded my VPS to 2GB, otherwise 1GB was enough), and the leftover docker images use up a lot of disk space. My main beef was with the time commitment, it ate into my already limited time budget.
* I have to keep reauthenticating for my side projects, which is a drag.
* A lot of these arguably internal sites are accessible over the internet because I didn't have a better way of doing things.
* I can't easily access these sites from my phone without setting up cumbersome port forwards and typing in IPs each time. This makes it hard to test on mobile without actually deploying to production.

## The new, secure setup!

Here's how the workflow is now:

{{ macros::image(src='/static/img/2022/06/new_infra.png', caption='My new infrastructure setup. Full of rainbows, unicorns, and happiness') }}

Instead of covering the whole image again, I'll focus on the changes:

* The `drone runner` is now on my local machine. Builds now take under a minute, which is great for my sanity!
* All traffic between hosts is now over `tailscale`, so the internal only services are, well... internal.
* I no longer have to authenticate to my side projects - `tailscale` takes care of that for me!

Let's go into how I set that up, from scratch. I won't go into every single detail of what I did or how to use these tools (nor a lot of the false starts), but will try to cover enough that someone can replicate this setup.

## Setting up a basic cross-machine source control + CI system

I set up `gitea` using the [docker container approach recommended on the docs](https://docs.gitea.io/en-us/install-with-docker/); and did the same thing for `drone` using [the instructions](https://docs.drone.io/server/provider/gitea/).

In particular, the hosts used were `git.mhlakhani.com` and `drone.mhlakhani.com`, with corresponding sites enabled on `nginx` and SSL certificates configured using `letsencrypt`.

Once this was all setup, I installed the `drone runner` on my desktop [following this guide](https://docs.drone.io/runner/docker/overview/) so I could run builds on my machine.

Builds worked fine! But I couldn't deploy anymore. 

## Schlepping builds over the internet

My deployment process uses `ansible` to do the following:

* Check out the repo for the project, and compute the hash of the latest revision on `main`
* Tag the `docker` image for the project with tag `$HASH` as `latest`
* Do a `systemctl restart $project` which would use `docker-compose` to deploy the (new) latest image.

This implicitly relied on the host already having the image on it. That was no longer true though.

How could I get images over? This was going to be a bit tricky, or so I thought.

I lucked out in that the upcoming version (1.17) of `gitea` provides a `docker` container registry. I upgraded my install to use the `dev` branch. With a registry in place, I could change my `.drone.yml` to push images to the registry, and my `docker-compose.yml` to fetch from there. Here's what I had to set up in my `drone` config:

<pre class="language-yaml">
<code class="language-yaml">
- name: generate_tags
  image: rustlang/rust:nightly
  commands:
    - git rev-parse HEAD &gt; .tags
  when:
    branch:
      - master
    event:
      - push
  
- name: build_docker
  image: docker:dind
  volumes:
  - name: dockersock
    path: /var/run/docker.sock
  commands:
    - docker build -t git.mhlakhani.com/mhl/khel:$(cat .tags) --rm=false .
  when:
    branch:
      - master
    event:
      - push

- name: push_docker
  image: docker:dind
  volumes:
  - name: dockersock
    path: /var/run/docker.sock
  commands:
    - docker login --username $USERNAME --password $PASSWORD git.mhlakhani.com \
    && docker image push git.mhlakhani.com/mhl/khel:$(cat .tags)
  environment:
    USERNAME:
      from_secret: docker_username
    PASSWORD:
      from_secret: docker_password
  when:
    branch:
      - master
    event:
      - push
</code></pre>

Note that I had to add a few secrets for each repo for the docker username and password (which is the same as that for my `gitea` user). Not great, but this works!

Lastly, I had to update my `nginx` config for this site to add a `client_max_body_size 128M;` to allow large uploads.

This setup *mostly* worked fine (modulo a few config options I left out) and would be enough, but I wanted these sites to stay internal. So I had to do more.

## Keeping things internal

The next step was to install `tailscale` in five different locations:

* On my windows desktop (where I access sites)
* Inside `wsl` on my windows desktop (where I develop)
* The docker desktop extension on windows, for the `drone runner`
* On my vps host
* On my phone

I then updated my `nsd` configuration so that the hostnames `git.mhlakhani.com` and `drone.mhlakhani.com` only resolve to internal tailnet IPs that are accessible on the network but not outside. I also accordingly changed the `listen` ports in my `nginx` config; and changed the docker compose files to make the services listen on the tailnet IPs as well.

All connections are now secure, and I can access sites easily from my phone too! Right?

Not so fast. Unfortunately this broke something.

My VPS host was using `systemd-resolved`, which propagates to the `docker` containers. Both `gitea` and `drone` were running on the same host, and when they'd try to resolve each other, it would be too smart and return `127.0.0.1` which would break networking as they'd try to connect to the port inside the container.

To fix this I had to override the `nsd` dns server entries for both of these to point to my DNS server directly, which would resolve to the tailnet IP and things then worked fine. This is a straightforward change:

<pre class="language-yaml">
<code class="language-yaml">
dns:
    - 138.68.243.212
    - 8.8.8.8</code></pre>

## Getting rid of logins

Ok, so now we have builds and deploys! But I still have to authenticate to my internal sites, and typing in usernames/passwords is a bit boring. Wouldn't it be great if I didn't have to? Well, with `tailscale`, it's possible!

Recall I'm using `nginx` still as a reverse proxy infront of all my sites. I was able to use [the tailscale nginx auth plugin](https://tailscale.com/blog/tailscale-auth-nginx/) to automatically login users from my tailnet.

Here's what the relevant portion of my nginx config looks like for `git.mhlakhani.com`:

<pre class="language-nginx">
<code class="language-nginx">location / {
        satisfy any;
        # Allow drone
        allow 172.19.0.0/16;
        deny all;

        auth_request /auth;
        auth_request_set $auth_user $upstream_http_tailscale_user;
        auth_request_set $auth_name $upstream_http_tailscale_name;
        auth_request_set $auth_login $upstream_http_tailscale_login;
        auth_request_set $auth_tailnet $upstream_http_tailscale_tailnet;
        auth_request_set $auth_profile_picture $upstream_http_tailscale_profile_picture;

        proxy_set_header X-Webauth-User "$auth_user";
        proxy_set_header X-Webauth-Email "$auth_user";
        proxy_set_header X-Webauth-Name "$auth_name";
        proxy_set_header X-Webauth-Login "$auth_login";
        proxy_set_header X-Webauth-Tailnet "$auth_tailnet";
        proxy_set_header X-Webauth-Profile-Picture "$auth_profile_picture";
        proxy_pass http://localhost:3002;
}

location = /auth {
        internal;

        proxy_pass http://unix:/run/tailscale.nginx-auth.sock;
        proxy_pass_request_body off;

        proxy_set_header Host $http_host;
        proxy_set_header Remote-Addr $remote_addr;
        proxy_set_header Remote-Port $remote_port;
        proxy_set_header Content-Length "";
        proxy_set_header Original-URI $request_uri;
        proxy_set_header Expected-Tailnet "m-hasnain-lakhani.gmail.com";
}</code></pre>

There are a few things there that don't directly follow the blogpost that I thought I'd highlight:

First, I had to add a hack to allow `drone` to access `gitea` as the connection isn't over my tailnet (it's on the same machine, I didn't want to install `tailscale` in each container).

Second, I also set `X-Webauth-Email`. I use google login for my `tailnet` so the `tailscale` username is my gmail address, while I have much shorter usernames on `gitea` and I didn't want to change them. This was a conundrum. Couldn't I use my email to authenticate instead?

`gitea` does not support that yet, but [the feature was easy to add](https://github.com/go-gitea/gitea/pull/19949) and I'm hopeful it makes the cut for 1.18. For now I deployed a version of `gitea` with this commit.

With these changes in, I no longer have to login to access `git.mhlakhani.com` while I'm on my tailnet. And, if I'm not on the tailnet, I can't access it! `drone` also uses `oauth` with `gitea` to login there, so all I have to do to login is click `Continue` on the home page.

## Can we get rid of logins for side projects too?

You can, actually! The long way around is to have the app directly talk to `tailscale` (like the nginx extension does) but if you're using the `nginx` setup like I am, all you need to do is read the `X-Webauth-User` or `X-Webauth-Email` headers.

For a `Rocket` app like my reads site, this was fairly easy to add to my `AdminUser` guard:

<pre class="language-rust">
<code class="language-rust">
// Lastly, try webauth
// Do we have a header that matches?
return match request.headers().get_one("X-Webauth-Email") {
    Some(email) if email == config.webauth_admin_email() =&gt; {
        let user = load_user(email)?;
        Outcome::Success(user)
    }
    _ =&gt; Outcome::Failure((Status::Unauthorized, ())),
};</code></pre>

I wanted to test this end to end locally, before deploying. But I was too lazy to set up `nginx` on my development machine just for this.

`tailscale` came to the rescue again. I simply added a `reads.dev.ts.mhlakhani.com` internal-only domain and copied my existing `nginx` config, and just made it forward to the internal ip of my `wsl` container. I could then hit that URL in my browser and verify it all worked.

The flow was a bit longwinded:

* My browser on my desktop connected to my VPS host
* My VPS host forwarded that to the WSL container on my desktop which returned a response
* This was then proxied back to my browser

But it works seamlessly and is so easy to use!

I then realized I could secure my side project even further: I created a `reads.ts.mhlakhani.com` internal-only domain and nginx config, using the same auth settings as discussed above. But I changed it so that the admin endpoint is only available on the tailnet, and if I hit `reads.mhlakhani.com/admin` (off tailnet), it returns a 403.

## Do we even need SSL now?

`tailscale` uses `WireGuard` and makes sure connections are encrypted, so in theory SSL is no longer needed and I could serve all my content over http and avoid bothering with certificates.

I started to do that, but ran into a few problems. First I'd still have to click past all the browser warnings regarding unsafe access (a bit annoying). Secondly, I had to add an `insecure-registry` option to all the machines accessing my `docker` registry. Lastly, and most annoyingly, [docker still needs the registry to listen on port 443](https://github.com/distribution/distribution/issues/2862).

So I decided to go back to using SSL. Everything worked and it was great!

Or so I thought. I remembered that I had pre-existing certificates for most of these domains. Now that they were internal only, `letsencrypt`'s automatic certificate renewal over `http-01` challenges would no longer work (as it couldn't connect). 

I had two options:

1. Switch to using the `tailscale` domain names everywhere for my machines.
2. Get `letsencrypt` certificate renewal working somehow.

I ended up going with the second option as I didn't want to change how I remember domains (and they are shorter). This was possible since I host my own DNS.

The solution was to use the `dns-01` challenge with a custom script to update the relevant `TXT` records. I would normally recommend using [this script](https://github.com/AlbertWeichselbraun/certbot-nsd-hook) but it didn't work for me as all my subdomains were just `A` records and not full blown zones.

I ended up cooking up a simple python script for this (based on that code) and using it with certbot:

<pre class="language-python">
<code class="language-python">
#!/usr/bin/env python3

# To test:
# sudo certbot certonly --dry-run -d reads.ts.mhlakhani.com \
# --preferred-challenges dns --manual \
# --manual-auth-hook="/etc/nsd/letsencrypt-challenge.py" -v

from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import os

def next_serial(n):
    base = datetime.now().strftime('%Y%m%d00')
    # day changed
    if int(base) &gt; int(n):
        return base
    # Assume we don't do &gt;100 a day
    else:
        return str(int(n)+1)

def update(zonefile, domain, challenge):
    path = Path(zonefile)
    shutil.copy(path, Path(zonefile + '.bak'))
    lines = path.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.find('; serial number') != -1:
            serial = line.strip().split(';')[0].strip()
            serial = next_serial(serial)
            lines[i] = f'           {serial}  ; serial number'
        if line.find('_acme-challenge') != -1 and line.find(domain) != -1:
            lines[i] = f'_acme-challenge.{domain}. 60 IN TXT "{challenge}"'
    lines.append("")
    path.write_text('\n'.join(lines))

certbot_validation = os.getenv('CERTBOT_VALIDATION')
certbot_domain = os.getenv('CERTBOT_DOMAIN')

if certbot_validation != None:
    update(f'/etc/nsd/mhlakhani.com.zone', certbot_domain, certbot_validation)
    subprocess.run(['systemctl', 'reload', 'nsd'])
    subprocess.run(['systemctl', 'reload', 'nginx'])
</code></pre>

This script automatically updates the relevant `TXT` record with the challenge and reloads the `dns` server so letsencrypt can verify I own the claimed domain and issue a certificate.

Everything can use SSL now and I don't have any warnings to click through!

## Conclusion

It can be hard to set up personal developer infrastructure that's 1) productive, 2) easy to use and 3) secure. But it's definitely possible to do it, and tools like `tailscale`, `gitea`, and `drone` are easy enough to use that you can set them up in a day or two. You can then focus on truly enjoying side projects and being as productive on them as at `$DAYJOB` (with their developer infrastructure team(s)). Hopefully this guide helps you do that!

*Many thanks to [@maisem_ali](https://twitter.com/maisem_ali) for providing feedback on this post.*