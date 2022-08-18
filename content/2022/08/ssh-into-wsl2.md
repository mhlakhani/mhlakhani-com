{
    "route": "post",
    "title": "How to SSH into WSL2",
    "date": "2022/08/18",
    "tags": ["tailscale", "note-to-self", "wsl", "infrastructure"],
    "excerpt": "How I set up SSH into WSL2 on my desktop and saved money on a new machine with this one weird trick."
}

As mentioned in a [previous post](/blog/2022/06/personal-developer-infrastructure/), I mostly use a beefy desktop at home for coding. But I'm not always at that desktop and sometimes the urge to code is too hard to resist. I'd love to be able to access this machine for coding while on any device on the go - in particular, I'm on the market for a new laptop and would rather not deck it out just for the *occasional* coding I'd do on it. So I went hunting to see if there was a way I could have my machine (and the WSL2 environment) accessible remotely.

This post is mostly intended as a note to myself in case I need to redo this setup.

## Route 1: SSH directly into Windows and pull up a WSL2 terminal. Doesn't work.

I first tried the instructions from [this blogpost](https://www.hanselman.com/blog/the-easy-way-how-to-ssh-into-bash-and-wsl2-on-windows-10-from-an-external-machine) as it seemed very promising and easy to use. The PowerShell commands were fairly straightforward (duplicating here to preserve them):

```
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Get-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\WINDOWS\System32\bash.exe" -PropertyType String -Force
```

Unfortunately, this no longer works, as pointed out in [this github issue](https://github.com/microsoft/WSL/issues/8072). This issue is fundamental and pointed out [in the release notes](https://docs.microsoft.com/en-us/windows/wsl/store-release-notes) so I have no hopes yet of this being fixed in time for my needs.

So, I reverted my default shell back to powershell:

```
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
```

## Route 2: SSH into WSL2 by coming in via the Windows machine. A bit roundabout, but works.

[This other post on the same blog](https://www.hanselman.com/blog/how-to-ssh-into-wsl2-on-windows-10-from-an-external-machine) advertised another way of doing it: using portforwards to expose openssh running on wsl via the host. It looked a bit complicated so I went to a variant of the same approach: Using SSH as a jump host.

I set up SSH on the windows host (as above) and inside WSL.

I then SSH'd into windows -- after adding my keys both to `C:\Users\mhl\.ssh\authorized_keys` *and* `C:\ProgramData\ssh\administrators_authorized_keys` on windows (and setting proper permissions on the latter - [from this post](https://www.concurrency.com/blog/may-2019/key-based-authentication-for-openssh-on-windows)):

```
$acl = Get-Acl C:\ProgramData\ssh\administrators_authorized_keys
$acl.SetAccessRuleProtection($true, $false)
$administratorsRule = New-Object system.security.accesscontrol.filesystemaccessrule("Administrators","FullControl","Allow")
$systemRule = New-Object system.security.accesscontrol.filesystemaccessrule("SYSTEM","FullControl","Allow")
$acl.SetAccessRule($administratorsRule)
$acl.SetAccessRule($systemRule)
$acl | Set-Acl
```

This let me get into windows. From there I could `ssh` into WSL and be on my merry way.

SSH supports jump hosts though and that made things much easier - all I had to do was add this config on my client machine:

```
Host mhl-desktop
    User mhl
    IdentityFile ~/.ssh/id_ecdsa

Host mhl-desktop-wsl2-jump
    User mhl
    IdentityFile ~/.ssh/id_ecdsa
    HostName localhost
    Port 2222
    ProxyJump mhl-desktop
    LocalForward 3009 127.0.0.1:3009
```

This proxies the connection via the windows host so on my client machine all I need to do is `ssh mhl-desktop-wsl2-jump` and it all works. And I can forward the ports I need to make them accessible.

### Aside: starting wsl and ssh automatically on boot

There is one downside to this approach - I can only access the machine after I've started the ssh server and WSL - since WSL doesn't support systemd this is hard to automate. I tried [the approach here](https://techbrij.com/wsl-2-ubuntu-services-windows-10-startup) but couldn't get it to work.

After more searching I realized that WSL2 [now supports boot commands](https://docs.microsoft.com/en-us/windows/wsl/wsl-config#boot-settings) so I added an `/etc/init-wsl.sh` and made that my boot command:

```
#!/bin/bash
service ssh start
```

I have docker desktop running which starts WSL automatically on boot, and this ensures SSH starts up. I can then boot my windows machine and SSH into WSL without ever starting the machine up!

### Aside to the aside: Can I boot the desktop on demand?

This is great when using the desktop from a laptop! But I still have to go to my room to hit the power switch which isn't great. I'd love to avoid that (I don't want to keep it on all the time, that wastes power).

... turns out there is something called Wake-on-LAN. After enabling it in the BIOS, I had to enable it on windows 11, [per this guide](https://www.groovypost.com/howto/enable-wake-on-lan-on-windows-11/):

* Open Device Manager
* Find your network adapter in the `network adapters` section
* Right click and select "properties"
* Go to the power management tab, check all options, including the magic packet one
* Go to the "advanced" tab, scroll to the "wake on magic packet" and enable that

Then run `ipconfig /all` in PowerShell to get the mac address, and you're in business!

I used an iphone app on my phone and confirmed I can boot the desktop up using it - that solves my problem.

## Route 3: Tailscale!

the above solution works, but it's kind of janky (exposing my windows host to the world) and annoying (need to forward ports and remember what to forward). Is there an easier solution? YES!

For a while I didn't try tailscale within WSL2 because I was blocked on [this github issue](https://github.com/tailscale/tailscale/issues/4833). I managed to find a workaround, and, well, it's glorious. I can just `tailscale ssh mhl-desktop-wsl2` and it all works. No ssh key configuration needed either!

I just updated my init scripts to launch tailscale on startup. `/etc/init-wsl.sh` is now:

```
#!/bin/bash
echo "initializing services"
sudo ip link set dev eth0 mtu 1500
service ssh start
bash /etc/start_tailscale.sh
```

And the referenced script is:

```
#/bin/bash
# Start tailscale daemon automatically if not running
RUNNING=`ps aux | grep tailscaled | grep -v grep`
if [ -z "$RUNNING" ]; then
    sudo tailscaled > /dev/null 2>&1 &
    disown
fi
```

To further aid working remotely and connecting, I eventually plan to set up a low powered raspberry pi node running tailscale, and using tailscale to wake my PC over LAN if needed. I'm eagerly following [https://github.com/tailscale/tailscale/issues/306](this github issue) for that support. I tried invoking the `peerapi` directly using the code [in this PR](https://github.com/tailscale/tailscale/pull/4536) but unfortunately the only other tailscale device I have right now is my iphone and that didn't seem to work. Setting it up on a pi is left as an exercise for the future.

Ah well. At least this still saved me a few hundred bucks on a laptop!