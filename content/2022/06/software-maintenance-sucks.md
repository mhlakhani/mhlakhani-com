{
    "route": "post",
    "title": "Software maintenance is annoyingly complex: a rant",
    "date": "2022/06/07",
    "tags": ["software", "maintenance", "rant"],
    "excerpt": "Why is software maintenance so hard?"
}

Today, we interrupt your regularly scheduled tech and engineering content for a rant.

Like a lot of tech folks, I have a bunch of personal software to maintain: a VPS server (hosting this blog), a bunch of side projects, etc. And, unashamedly, I'm often too lazy to keep everything totally up to date. There's many of us out there! We just want to Get Shit Done (tm) and not have to worry about maintenance.

Until all that tech debt comes true with interest, and we have to declare bankruptcy.

## The problem

I pay for a relatively underpowered VPS on DigitalOcean - after all, 2GB RAM and 2 CPUs should be more than enough for anybody! With careful choice of what to run, that can go a long way: I host this blog, two webapps, a git host, CI, monitoring, and a few other random things on it. Why pay for more if I can avoid it?

This setup has worked fine for years - everything works smoothly, except for when I push out some code to a side project and need to upgrade the Rust version. A full CI run which includes builds, tests, and a release build, often takes >30m to accomplish on this wimpy machine. I had to upgrade from the $5 to the $10 plan at one point due to OOMs, but I refuse to pay any more than that.

I set out to accomplish (what I thought was) a relatively straightforward task: updating my CI setup to utilize the powerful machine I have at home: wouldn't it be great if the actual CI builds could run on my machine, with everything else the same way? And, to boot, wouldn't it be great if I could keep this connection fully secure using [tailscale](https://tailscale.com/)?

Much easier said than done.

## The (attempted) solution

A day and a half later, I'm *mostly* through the fallout in terms of work items, but I expect it'll be a couple of weeks before I've recovered from this.

I started by going over the docs for [drone](https://www.drone.io/) and reading how to launch an extra runner. It became clear that the version I was on (0.8) was too old, and I needed to upgrade to a newer version to keep things going. So, I spent some time migrating over to drone2, and setting up a runner on the VPS to keep the old behavior initially.

That started to run into issues communicating (specifically: webhook issues) with my git service, [gogs](https://gogs.io/), and builds no longer worked. That ran into even more issues (lost to time). gogs has been superceded by [gitea](https://gitea.io/en-us/) in many aspects, so off I went trying to upgrade and see if that fixed the problem. Installing it was fine, but migrating was really painful. At the end, I had to resort to manually importing each repo one by one. With 20 odd repos and a dozen or so clicks to migrate each repo, I grabbed a snack and off I went.

Once things were migrated, I was able to connect drone to gitea, push a commit, and trigger a build. Yay, things worked!

Except they didn't. I still needed to set up the runner on my local machine.

## The rabbit hole

Here's where the (not so) fun began. To avoid making this post too long, I've summarized the issues and solutions:

* Setting up a local runner:
  * This was actually easier than I thought. I set up the runner locally as a docker container, pointed it to the remote host (using the tailscale hostname - tailscale was the only thing that worked out of the box here!), and verified it could run things. However, the resultant docker images lived on my local machine, and not on the VPS, and I'd need to schlep them over. This was a problem.
* Getting builds actually sent to the local runner:
  * Turns out runner priorities/ordering [isn't supported well in drone](https://gitea.io/en-us/). The easiest solution I found for now was to disable the remote runner, so builds always go to my local machine. For my use case, this should work fine 99% of the time.
* Getting docker images on the VPS:
  * I lucked out here. Turns out the latest version of gitea, 1.17 (currently in developer mode) supports being a docker registry. I upgraded, and ran `docker push` locally to confirm I could send images over and fetch them. Time to get these running in my drone pipelines (and find out they don't work!)
* Fixing the webhook:
  * After upgrading to gitea 1.17-dev, webhooks started breaking. Test events would work, but post commit webhooks would not run no matter what I tried. This took a lot of diagnosing before I gave up and took a break.
* Attempting to get authentication working using tailscale:
  * Part of the goal of this upgrade was to use tailscale more to secure my connections. I looked at this [blog post](https://tailscale.com/blog/tailscale-auth-nginx/) and set up the service and the relevant nginx configuration and ... nothing worked! Turns out the service unit is not supported on my VPS on 16.04 which is too old. I filed a [quick bug report here](https://github.com/tailscale/tailscale/issues/4817).
* Upgrading ubuntu:
  * It had been so long, I figured I might as well upgrade my machine. I was more confident in doing it now since most of the setup and config was backed up on ansible so I knew what to move, and the data was safe using DigitalOcean backups. However, this didn't work.
  * First off, the `do-release-upgrade` itself refused to run as it kept saying I needed to upgrade packages locally.
  * Then it failed to find a package needed to upgrade. Some googling later suggested that the system was too old to ugprade, and [there was a workaround](https://www.digitalocean.com/community/questions/cannot-update-to-19-04-the-essential-package-ubuntu-minimal-could-not-be-located-2)
  * That kicked off the ugprade, but half the packages failed to install due to some conflicts or issues. I had to fix up about thirty or so manually (reinstalling the .deb, finding a package, etc) before I had a system running 22.04
* The new system works fine, right? Nope!
  * After upgrading, nothing worked! I couldn't browse to sites on my server, though thankfully I could ssh in as my ssh config specifies the server IP not host.
  * After getting in, I found the dns daemon (`nsd`) wasn't starting because `systemd-resolved` was now listening on port 53. Some fighting later, I managed to make them coexist.
  * More attempts later, I learnt most host resolution was broken as I tried to install packages. Disabling `systemd-resolved` made things work, but then I couldn't connect to hosts on my tailnet (not great).
  * Even more attempts later, I got this working (don't ask me how), or so I thought.
* Getting docker back
  * Installing docker on the new system failed, as the service failed to start up. Much googling later, I found out that the newer versions of docker/ubuntu no longer support `aufs`, so all my old images were gone. Whoops. The easiest way to get things back was to toss out the install and start afresh
  * With publicly available images, I could get my git hosting, CI, and monitoring services back.
  * During testing, however, I found that drone CI could no longer connect to my git host. After a painful few hours of debugging and reading [this blog post](https://tailscale.com/blog/sisyphean-dns-client-linux/) and digesting it I found out that `systemd-resolved` would resolve `mhlakhani.com` to 127.0.0.1 when resolved from the host, which makes sense, but doesn't work for a docker container as it would try to access the port inside the container. I had to override the DNS for just that container so things would work.
  * At least now I could get back to getting my CI working. Magically, the webhooks started to work!
* Getting docker images on the VPS, take 2:
  * I changed my drone CI pipelines to end with a `docker push` command to push the images over. With some fighting over permissions (needed to `docker login` inside the container each time, which isn't great), I could get the images over to the registry, and my VPS can pull from it when deploying projects.
  * Image uploads broke for my larger projects. I had to go down and edit my nginx config to allow for larger request bodies to make this work.
* At this point, I'd surely be done, right?
  * Kinda. I was able to rebuild my projects by sending out updates to their CI configs (pointing to the registry), getting new images on the host as a result and pushing them out
  * But for `reads.mhlakhani.com` (currently down at the time of this writing) this didn't work.
  * Turns out the code [no longer compiles on the latest rust nightly](https://github.com/SergioBenitez/Rocket/issues/2203), and the solution is to upgrade to the newer version of Rocket. Which I started doing, and hit a few hundred compile errors. This migration won't be as straightforward as the wiki suggests, since I'm using a bunch of unsupported libraries (e.g. need to migrate from `askama` to `tera`) so I expect a few weeks are needed to finish this, given the time I'll be able to dedicate.

... And that's where we're at now.

## Parting thoughts

I write software for a living and (mostly) enjoy sysadmin tasks; but this had me at my wits end for quite a while. How is the average person supposed to write software to do their day job, providing valuable products for people, without spending half their lives just maintaining software and systems that constantly break?

As a security practitioner I often see people talk about the importance of constantly patching, and upgrading, and often times (sadly) making fun of people who don't patch immediately. But things take time, and this toll adds up.

How can we do better here? This isn't a sustainable solution, though I have no answers to offer right now. Need to go back to upgrading my software so it still works.

At least I can push out new builds faster when it's done!