{
    "route": "post",
    "title": "On being a staff engineer",
    "date": "2022/08/08",
    "tags": ["work", "management", "career", "facebook", "staff-engineering"],
    "excerpt": "On career growth, what it means to be a staff engineer, and how to get there.",
    "featured": true
}

I've had a few conversations recently with folks on what it means to be a staff engineer and how to grow into the role. A few common themes emerged so ... time for a blog post! Hopefully this will be a useful conversation-style braindump for others. This is what I usually cover during an ~hour long conversation, but without the "let's tailor this to your specific situation" special sauce.

> NOTE: This is just, like, my opinion, man. There are many equally valid ways to grow as a staff engineer and expectations vary widely by company and person, some places don't have as supportive of an environment, etc. The themes I'm highlighting *should* be general enough, but make sure to apply the right advice to your situation. I'm happy to offer more tailored advice in a private setting.

## What is a "Staff" engineer anyway?

> You know a staff engineer when you see one.

For a long time, as I struggled to understand what the staff engineer role entailed, I'd hear versions of the above quote and want to pull my hair out. It's tautological. It didn't make one iota of a difference in telling me how to get there. I'd especially want to flip a table when people told me "if I have to tell you what to do to get there, that proves you're not a staff engineer".

Over time, I learned to see the profound truth behind it. Going from a senior engineer to a staff engineer involves a huge change in mindset and how you approach work. If you keep trying to become a "better" senior engineer, you may never reach the staff level. It's a different job. Armed with that knowledge, I looked at various examples of staff+ engineers, saw how they would work and how different it was from how I would work, and tried to emulate their behaviors.

This isn't super helpful, though, so let's try to make it more concrete.

### Aside: engineering career ladders at Big Tech

One way to visualize what a staff engineer does is to compare the role to more junior engineers. I'll elaborate on Facebook's career ladder (as I'm most familiar with it) -- other big tech companies are similar from what I understand. Here is a *very simplified version* of this that I have used in the past, with a ton of disclaimers applied - thinking about the levels in terms of scopes of ownership:

* E3: New grads and entry-level engineers join at this level. At this level, you are expected to be given *tasks* (each a few days of work) to do, and do them well. 
* E4: A mid-level engineer. At this level, you're expected to be a bit more independent - you get assigned *features* to ship (a couple of months or so of work at a time), are expected to break those down into tasks and prioritize accordingly, and deliver them.
* E5: A senior engineer. You're expected to own a small system/product, lead a few other engineers potentially, and be a source of continuing impact. You're given open ended problems to solve on a larger time scale (> 3 months typically), and you go ahead and solve them. To a first approximation, your manager should be comfortable going away for a month and knowing that you'll keep yourself busy doing useful work - finding more work to do as needed. Your ownership and responsibility is likely limited to the system you're responsible for - and maybe at the team level, but usually not at the org level.
* E6: A staff engineer. You're expected to own an *area*: solving important business problems for your org and team. You're responsible for identifying new problems worth solving, bringing people onboard to solve them, and nailing project delivery. Your influence extends beyond your immediate team and onto your partner teams in the org.

You can read a bit more about this on [The Pragmatic Engineer's blog on career paths](https://newsletter.pragmaticengineer.com/p/engineering-career-paths). I'm hoping to have a more detailed writeup on this at some point in the future.

### Okay, but that was still vague. What does a staff engineer *do*?

For me, the key difference between a senior engineer and a staff engineer is the trifecta of *ownership*, *accountability*, and *leadership*:

* *ownership*: As a staff engineer, you own and are responsible for a broad *area* of impact. This likely goes beyond your immediate team and into org-level goals. You are responsible for setting the direction of the product/team/area. 
* *accountability*: The buck stops with you. You're responsible for *results* - and I don't mean just building code or systems. You're responsible for org-level impact and moving whatever metric is important (revenue, user growth, whatever it is). At the end of the day, you write code to solve business problems, and this is the first level where you're truly accountable for whether that business impact was realized or not. No excuses.
* *leadership*: You demonstrate technical and personal excellence, setting a high bar for others to follow. You motivate people to do their best work and get them excited about contributing to your projects. People look up to you as a source of ideas and inspiration.

In short, you're the opposite of this:

{{ macros::image(src='https://imgs.xkcd.com/comics/not_enough_work.png', caption='A staff engineer always has useful work to do.') }}

Personally (and I was lucky here), these three boiled down to one thing: Giving A Shit and taking pride in my work. I want to be proud of my work, both in terms of the technical achievements and the end results, which leads to taking ownership over what I do, and holding myself accountable for success - and then leading by example naturally follows.

In my experience this trifecta is the most common *necessary* (but not necessarily sufficient) requirement for being a staff engineer. There are other archetypes, of course, where you're not necessarily a tech lead lead - you can drive a complex cross-team collaboration, be a highly specialized expert in a complex domain, etc.

[Here is another take on what staff engineers do, from the Staff Engineer blog.](https://staffeng.com/guides/what-do-staff-engineers-actually-do)

### That can't be all, can it?

The above is still kind of high level. But if you're able to nail it you're almost there. It's hard to be comprehensive, but here are some more common traits of staff engineers and how they approach work:

* *Direction*: You consistently identify impactful areas of work, and have a track record of delivering useful business results. You work on what matters - and when it stops mattering, you stop working on it.
* *Scope*: Your work likely spans beyond your immediate team and impacts the broader org. You don't confine yourself to the boundaries of what your immediate team is *supposed* to do.
* *Ability to handle ambiguity*: If the problems you face don't make you go "oh shit, how the hell do I even approach this"? you may not be there yet. Staff level problems are often complex, unclear, and influenced by chaotic situations.
* *Delivery*: You deliver projects on time, working with other people (across various disciplines if needed) to get things done. You see projects through to the end, ensuring they produce results.
* *Coordination*: You can manage a project, breaking it down into work items, delegating work as needed to others, providing status updates and communicating downwards, upwards, and sideways, as needed.
* *Collaboration*: You build relationships across teams so you you can all work *together* towards shared goals, and avoid duplicate/inefficient work.
* *Ownership*: When a problem arises, you jump towards the fire and raise your hand to fix it, rather than going "it's not my problem".
* Summarizing the above, you consistently identify the right (really challenging!) problems to solve, make yourself responsible for them, and solve them really well.
* *Master of your craft*: You demonstrate technical excellence and expertise in your domain, and you're often the person solving the hardest technical problems in your area.
* *Bar raiser*: You hold your work to a high standard and hold others to the same high standard. But you're not an asshole - you help them improve through empathetic mentoring.
* *Team player*: You take the time to make the team around you better - finding inefficiencies, communication breakdowns, etc - and making everyone more efficient.
* *Mentorship*: You find opportunities to mentor and improve the people around you - and are consistently sought out for your advice.
* *Glue*: You're the glue that keeps the team together when needed. (NOTE: This is risky and prone to backfiring unless you have backing from leadership. [Read more here](https://noidea.dog/glue))
* *Risk taker / explorer*: You take calculated risks on new ideas, finding the Next Big Thing that results in a huge improvement for the team. You know when to cut your losses on a failed idea.
* *Doing whatever it takes*: Sometimes the most important thing is not the code, but communication, testing, whatever. You're not "above" any work, you care about the end result and do whatever is needed to get things done. If you're coding a lot (you'll know what "a lot" is) - you may be doing it wrong. 
* *Self improver*: You take the time to gather feedback and are consistently improving yourself and challenging yourself.
* *Visionary*: You identify and drive the vision for work to be done - on a multi-year timescale, usually.
* *Prioritization*: You focus on the intersection of *important* and *urgent* work, often spending time on things you are uniquely suited to doing - and delegate everything else.
* *Expert communicator*: Underlying a lot of the above is an assumption that you're an effective communicator. You can clearly break down complex technical topics for people to understand, help ensure people are on the same page, and avoid miscommunication. Writing well is a huge superpower.

I know this is a huge list. There's a reason it takes a while to get to staff engineer (I definitely pushed myself before I was ready and it didn't go well), and you don't need to work on all of these at the same time. Take it slow and steady.

### But this is all fluffy people stuff. Where is the "engineer" in staff engineer?

Dear Lord, please stop me from facepalming. On a more serious note, I will admit I had the same perspective about this not too long ago.

At the end of the day, my take on it is this: without the people stuff, I would be a way worse engineer. What's left unsaid in the above is that technical mastery and excellence is a prerequisite for success at this level. However, through communicating, mentoring, and delegating I realized this: I can focus on harder, more challenging engineering problems than I ever have before - I've earned people's trust so I have the freedom to pick important problems to solve, I can delegate parts to others, and get exposure to a lot more technology than I would have if I siloed myself in one area.

It's just that the responsibilities and job changes slightly from pure engineering. This may not be for everyone (I certainly struggled with it even after I got promoted to senior), but don't for a moment think that you won't be doing engineering work.

## Getting to staff seems too hard. How do I even begin?

Now we're talking. It's hard, it will take time. I <s>nearly</s> burned myself out trying to get there, then realized it was more of a "work smarter, not harder" type thing. When I finally got there, it was such a nothingburger - because I'd focused on sustainable skills growth. Hopefully you can do the same.

This post would be three times the size (and it's already too long) if I covered all of the topics in detail, so I'll try to be brief here and write follow-up blogposts in the future.

### Work on your growth

Try to improve yourself a little bit every day. It may not seem like much in the short term, but just like compounding interest, it will pay off in the long term. You should constantly be growing - make sure your projects are challenging, and you regularly get to exercise your people skills.

Create a growth plan for yourself: Map out where you are today, where you want to be, and then find the skills you need to grow to get there. Work on each of those one by one. This is a great place for you to get feedback from your mentors and manager - they can provide input on things you have missed.

Take every opportunity you can to seek feedback. If you're waiting for others to proactively provide feedback, or for a performance review cycle, you're waiting too long. You should be asking your manager for feedback every 1:1, and asking others for feedback whenever it feels right (e.g. at the end of a project, or after a milestone, etc). If they think they don't have any actionable feedback, push for it: things may be going well (and people tend to just assume lack of negative feedback = no feedback) so ask explicitly for growth feedback: things like "how can I do better?", or "how could this project have gone more smoothly?".

Learn from your own work: At the end of every project, hold a mini retrospective. Think about what didn't go well, and how you could have prevented those things upfront. Think about what went well, and double down on those things in the future. Be creative: one project I launched went really smoothly upon launch - after much reflection, I realized we should have delivered it much faster because we over-engineered it (nothing broke, after all!).

### Avoid burnout

Remember that you're in this for the long haul. Don't burn yourself out trying to get there. Even if you push yourself to the limit and get that promotion now, what's next? Will you be able to operate at 120% for the foreseeable future? What about the example you're setting for everyone else that looks up to you as a leader?

Focus on sustainability. Yes, you will be the go-to person and be bombarded with questions that take up your time and attention. Recognize that that's part of the job now - not just what you can do individually. Take a note of patterns in how you spend time, find ways to optimize it, and delegate away as much as you can.

At the end of every week, reflect on your time and for each major activity, ask yourself: "was this the most important thing I could have been doing at this time? Could someone else have done this?". If the answer is yes, work towards delegating it, or growing someone else into being able to do it.

### Grow a team around you

A staff engineer should think in terms of "we" and not "me". You're responsible for more than yourself, like it or not. Own it, and thrive as a result - you can get so much more done with the right team.

Build a team: Identify the types of talent needed to deliver on your team's vision, and work with your manager to hire people. As people join, help them ramp up quickly, identify the right work for them, and keep them happy.

Motivate people to work: Don't just be the overlord who tells people what to do. Tell them *why* they are doing it, helping them feel ownership over the system (without necessarily being on the hook for it - that's your job). Motivated people work harder, do better, and are happier. And they will surprise you with what they can do.

Delegate: Make sure the right person is doing the right work at the right time. Set clear expectations for what they should do, follow up regularly to make sure things are on track, and slowly ramp up the scope of what you delegate so people get more self-sufficient.

Mentor others: Continuously provide feedback to the people you work with, and be intentional about their growth. Help them find opportunities for work that challenges them and gets them promoted. If they succeed, you succeed.

Share the praise - the wins are everyone's. It's a team effort. At the same time, own your mistakes. If something goes wrong, it's on you - don't try to pawn the blame off to someone else.

### (Over) communicate

I feel like communication is the main job of a staff engineer. Above all else. And I don't mean just speaking or getting others to listen to you. **The most important thing you can do as a staff engineer is shut up and listen**. Ask the right questions, get the information you need to succeed. Once you're sure you have the right information, communicate what you want / what should be done - clearly, concisely, and effectively. Whenever there is a miscommunication, reflect and think about how it could have been avoided.

Communicate sideways: Talk to your peers, both on the team and on the teams you work with. Talk to your users. Ask them what problems they face, and how you can help. You may not be able to help *right now*, but your subconscious mind can get to thinking. Talk about what work you're doing recently and where you need help - they may provide advice.

Communicate downwards: Talk to the people you mentor and support. Ask what they need help with, what they want to do next, and how you can make their lives easier. Learn about what frustrates them day over day - and then improve your team's processes to remove these roadblocks.

Communicate upwards: Talk to your manager and understand what they're worried about for the team. Ask how you can improve the team. Talk to your director and ask what keeps them up at night - and what org wide efforts you can contribute to. Ask about where your work falls short and what they would rather have you be doing instead.

All of the above also tie directly into a prerequisite for becoming a staff engineer: having great ideas and direction. The more you talk to people and listen, the more easily you'll be able to generate your next big project idea and continue providing valuable direction for the team.

### But I'm doing all of this and I'm not getting promoted.

It may feel like you have to just suck it up and be a people pleaser, focus on talking your work up rather than doing work, and give up "yourself" in order to get promoted. I've felt that way before. I've heard others express this frustration. There are certainly times when you see other people climb up the career ladder and it feels like that's what they're doing. First off - stop comparing yourself to others! Grow at your own pace, and value your own personality and morals. Would you rather be promoted and feel horrible regret for being a sellout, or would you want to earn it and do things your way? 

If you're not getting promoted, take a step back and ask why. Ask for feedback, and do not dismiss it - listen with an open mind. If people tell you you're not ready, ask for clarity on the expectations. You may hear back that an expectation for a staff engineer is to figure it out - that's okay! In that case, ask for resources or examples of people/work to look up to and start from there.

Work towards identifying staff level projects, and observe the work going on there and attach yourself to those projects. Slowly work towards making a "promo doc" highlighting what's expected of you before getting promoted, and get buyin from your management chain on it. Then, slowly but surely, start checking items off the list. Make sure to communicate throughout the process - explain *why* you're picking project X, get clarity on how it will improve things, and then communicate the wins you get, etc. It's not just about appearances -- this over communication ensures that you are doing the right thing and gives people a chance to give you feedback on your work. It's worth it, I promise.

Regularly set aside time to ask for feedback and make that explicit to your management chain. Make it clear that you are not "just" chasing the promotion, but that you want to grow and be more effective. Make sure to have mentors - ask your manager to find you mentors if you don't have any! - so you can broaden your horizons and get advice that's targeted to your specific environment. I wouldn't be where I am today without some great mentors.

Lastly, work on a [brag doc](https://jvns.ca/blog/brag-documents/)! Write down the work you've done and reflect on it. And get feedback on whether you're focusing on the right things. I tend to forget what I've done as I do a lot of small things - and noting things down is especially useful for capturing glue work and optimizing my time.

Doing this stuff may not seem worthwhile, but it adds up. You'll get there, slowly and steadily. And when you do, you'll look back and smile thinking about how hard it was back then and how easy it seemed at the end.

## Additional resources

* Addy Osmani has a [great post](https://addyosmani.com/blog/software-engineering-soft-parts/) on the soft parts of software engineering - crucial skills necessary for any staff engineer.
* Cindy Sridharan has a [great article](https://copyconstruct.medium.com/know-how-your-org-works-or-how-to-become-a-more-effective-engineer-1a3287d1f58d) on understanding how your org works and using that to be more effective. Given how important it is to navigate your org effectively as a Staff+ engineer, I highly recommend this one.
* The [Staff Engineer book](https://staffeng.com/book) is a great resource. I haven't read the book myself, but I have read a decent chunk [of the blog](https://staffeng.com/guides/) and the [cliff's notes for the book](https://github.com/mgp/book-notes/blob/master/staff-engineer.markdown).
* [Here's a blogpost on career growth from the author of the Staff Engineer book](https://lethain.com/mailbag-beyond-career-level/)
* [Here is a take on staff level engineering at gitlab](https://about.gitlab.com/blog/2020/02/18/staff-level-engineering-at-gitlab/)
* For those interested in growing as a Tech Lead, I wrote a [series of posts based on a course I wrote](/blog/2022/04/tech-lead-academy/) which may provide some tactical advice.

## Conclusion

Well, this was a long rambly post, but I hope it was useful. I'd love to edit this post with more information, and expand upon some of these in more in-depth articles - please reach out with comments and feedback, and opinions on which topics you'd like me to expand on first!