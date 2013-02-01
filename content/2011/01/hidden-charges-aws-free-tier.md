{
    "route": "post",
    "title": "Hidden Charges when using Amazon AWS' Free Tier",
    "date": "2011/01/05",
    "tags": ["AWS", "ramblings"],
    "excerpt": "Amazon charged me 1 cent. Let's find out why",
    "featured": true
}

{% from "macros.html" import image %}

If you follow the technology scene a fair bit, you might have heard of [AWS (Amazon Web Services)](http://aws.amazon.com/). If not, all you need to know is that it allows you to build powerful applications for use on the web. It could be likened to renting computers by the hour, in a sense (for the EC2 service). Being the geek that I am, I decided to give their free tier a spin a while back; and see for myself what all the hype was about. The [free usage tier](http://aws.amazon.com/free/) is great for learning the ropes, and, well, it's free. I fired up a few instances in the first few days, ran some basic code, tried it all out. So far, so good. Seamless experience, it seemed to live up to the hype.

And then a few days later, I saw the bill. I'd taken full care not to do anything outside the free usage limits, but it seems a charge had snuck by. Some sort of "Regional data transfer" charge.  

{{ image("/static/img/2011/01/bill1.jpg", "Exhibit A") }}

They had the audacity to charge me **a whole cent!** So, what IS Regional data transfer? From the Amazon EC2 pricing page:

> **Regional Data Transfer**  
> $0.01 per GB in/out - all data transferred between instances in different Availability Zones in the same region.  
> **Public and Elastic IP and Elastic Load Balancing Data Transfer**  
> $0.01 per GB in/out - If you choose to communicate using your Public or Elastic IP address or Elastic Load Balancer inside of the Amazon EC2 network, you'll pay Regional Data Transfer rates even if the instances are in the same Availability Zone. For data transfer within the same Availability Zone, you can easily avoid this charge (and get better network performance) by using your private IP whenever possible.

But wait. I'd only ever run one instance at the same time. There wasn't any data transfer between any of my instances...  
Digging through the very detailed usage reports, there was this single item of interest:

> AmazonEC2   InterZone-Out   DataTransfer-Regional-Bytes 1/3/2011 18:00  1/3/2011 19:00  417155  
> AmazonEC2   InterZone-In    DataTransfer-Regional-Bytes 1/3/2011 18:00  1/3/2011 19:00  47277245

Wait. I'd run a system update, and it had used about 45MB. Might that be it?  
Let's see. I installed mysql-server, adding another 23MB to the download usage. Sure enough, it showed up under Regional Data Transfer:

> AmazonEC2   InterZone-Out   DataTransfer-Regional-Bytes 1/4/2011 14:00  1/4/2011 15:00  267511  
> AmazonEC2   InterZone-In    DataTransfer-Regional-Bytes 1/4/2011 14:00  1/4/2011 15:00  23816600

{{ image("/static/img/2011/01/apt1.jpg", "The terminal session") }}
{{ image("/static/img/2011/01/bill2.jpg", "Exhibit B") }}

The item to note is the address of the update server, http://us-east-1.ec2.archive.ubuntu.com . Checking the repository sources, it seems AMIs have this automatically set as the default. Something about it makes me think it's in the US East region, which is where my instance was located as well. So, let's investigate.

First off, I thought it might be charging it under regional data transfer because it was using a public address. (see the quote from Amazon above) Hunting through documentation, I found the command to get the private IP, and put that in /etc/hosts. For confirmation, I installed mysql-server again, thinking "I'd love to see them charge me now!"

And they sure did:

> AmazonEC2   InterZone-Out   DataTransfer-Regional-Bytes 1/4/2011 16:00  1/4/2011 17:00  244771  
> AmazonEC2   InterZone-In    DataTransfer-Regional-Bytes 1/4/2011 16:00  1/4/2011 17:00  23878908

{{ image("/static/img/2011/01/bill3.jpg", "Exhibit C") }}

But that's only a temporary stop gap. It's not the proper way of doing things &#0153;. Let's try to find a work-around.

Then I noticed, even with all this bandwidth usage, the bill still stuck firm at one cent. Apparently, the bill is computed by rounding up your usage. So, as long as you keep your system updates under 1GB, you won't be charged more than a cent. Which is fine by me, so I undid all the /etc/hosts changes. Let's not burden the Ubuntu mirrors unnecessarily.

Now for the fun part: You might've noted that 1 cent is certainly such a small amount. Wouldn't it cost Amazon more in credit card fees? Why should they bother charging such a small amount? Well, it seems Amazon had the same idea. Looking at the statement for the last month again, I found this gem:

{{ image("/static/img/2011/01/bill4.jpg", "Exhibit D") }}

In short, if you were wondering and worrying about the small charge showing up on your 'free' trial of AWS services, you needn't worry anymore.

I'd like to thank Amazon for providing a great product and stuff to write about!

\- Hasnain
