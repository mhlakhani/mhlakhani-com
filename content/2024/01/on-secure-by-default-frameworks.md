{
    "route": "post",
    "title": "On Secure By Default Frameworks",
    "date": "2024/01/11",
    "tags": ["rust", "rocket", "security"],
    "excerpt": "Learn about writing secure by default frameworks and why they are important"
}


Switching between coding on one-man side projects versus coding professionally for work is an interesting experience. It's mostly a breath of fresh air as you get to work on a smaller codebase and have fewer constraints - so you can focus on the fun part. However, I found myself missing the internal guardrails (secure frameworks!) at $previous_employer which helped me be productive without spending too much time on security.

Recently, I spent some time reusing the same general "shift left" approach but tailoring it for my side project - [trackmy.games](https://trackmy.games) - you should try it out! - so I could keep it as secure as possible without investing a crapton of time. I've also open sourced the framework referenced in the post - you can see it on [github](https://github.com/mhlakhani/rocket_csrf_guard) or [crates.io](https://crates.io/crates/rocket_csrf_guard).

## Why are secure frameworks important anyway?

Why do I care so much about this if I'm just working on a side project? Well, stepping back a little, I hope you can agree that keeping a codebase secure is important for big companies. Don't take my word for it - here's a [blogpost from Meta](https://about.fb.com/news/2019/01/designing-security-for-billions/):

> In the graphic below, you can see how our “defense-in-depth” approach relies on a combination of technology, expert security teams and the wider security community to help protect our platform. In the following article, we’ll dive into each of these five components — secure frameworks, automated testing tools, peer and design reviews, red team exercises and our bug bounty program — in greater depth.

There's a literal army of people working on security there, yet bugs still get through. As a single developer using limited spare time on a side project, there's no way I can achieve that level of security. So, I tried to "shift left" as much as possible and get as much bang for my buck using frameworks. From that blogpost again:

> We also invest heavily in building frameworks that help engineers prevent and remove entire classes of bugs when writing code. Frameworks are development building blocks, such as customized programming languages and libraries of common bits of code, that provide engineers with built-in safeguards as they write code.

I don't have the budget for automated testing tools, design reviews, a red team, or a bug bounty program. I do, however, have time to write a framework so I can no longer (easily) introduce security bugs and make mistakes. And with some discipline (which is both easier and harder as a solo dev) we can go quite far with just a framework.

The remainder of this post will discuss the characteristics of a good 'secure by default' framework and how to create one.

## Ergonomics

One of the main lessons I learned at Meta is that it's not sufficient to write a secure framework: you can't just call it done once you've built it. The hard part is in getting people to use it. For that, you need to make it so good that people want to use it because it makes their lives easier - security comes second.

[Rocket](https://rocket.rs/), the web framework I use to build [trackmy.games](https://trackmy.games), doesn't support CSRF protection out of the box. And I (obviously) needed CSRF protection to make the site secure. So I looked around for alternatives, didn't find any library that made me happy, and went to write my own.

In my opinion, a CSRF library needs the following:

1. Token Generation: It should generate unique, random tokens for each session or request.
2. Token Embedding: It needs to provide a way to embed these tokens into forms.
3. Token Validation: It should validate the tokens on the server-side, ideally before processing the request.
4. Token Storage: It should support secure storage and retrieval of tokens.
5. Token Expiry: It should support invalidating tokens after a certain period of time.
6. Ergonomic integration with Rocket: It should have a clean, easy to use integration with Rocket.
7. Customization: All of the above should be customizable, ideally.

Most of the libraries I researched (not linking, I'm not here to blame!) fell short on at least one of these. Most commonly, they just weren't ergonomic enough.

### Standard ergonomics

The libraries I saw focused on token generation/embedding/validation, but left it up to the application developer to tie all of these together. Walking through an example (cleaned up from real code):

<pre class="language-diff-rust diff-highlight">
<code class="language-diff-rust diff-highlight">
// First, update the form definition...
#[derive(Debug, FromForm)]
pub struct MarkGameAsOwnedForm {
    platform_id: Platform,
    game_id: u64,
    // Add a csrf_token field to your form
+   csrf_token: String, 
}

// Then, update the route that shows the form...
#[get("/game/&lt;game_id&gt;")]
pub async fn view_game_info(
    game_id: i64,
    user: User,
    db: Connection
) -> Template {
    let game_data = fetch_game_data_from_somewhere();
    // Get a valid CSRF token (for the session, via a cookie, whatever)
+   let csrf_token = library::get_csrf_token_somehow();
    // And put it in the template
+   Template::render("my_template", context! { game_data, csrf_token })
}

// And update the route that processes the form...
#[post("/game/&lt;game_id&gt;", data = "&lt;post&gt;")]
pub async fn update_game_ownership(
    game_id: i64,
    user: User,
    post: Form&lt;MarkGameAsOwnedForm&gt;,
    db: Connection
) -> Result&lt;Template&gt; {
    // Remember to verify the CSRF token against what's expected!
+   library::validate_csrf_token_from_request_against_expected(&post.csrf_token)?;
    Template::render("my_template", context! { whatever_data_here })
}
</code></pre>

Of course, you also need to update your HTML template to add a `csrf_token` field. I've left that out for brevity.

This isn't great, there's 4 things you need to remember to do for each new type of form!

### So, how can we do better?

This is the pattern I follow in my code, now that I'm using [rocket_csrf_guard](https://github.com/mhlakhani/rocket_csrf_guard):

<pre class="language-diff-rust diff-highlight">
<code class="language-diff-rust diff-highlight">
// Use a macro to add the csrf token
+ #[with_csrf_token]
#[derive(Debug, FromForm)]
pub struct MarkGameAsOwnedForm {
    platform_id: Platform,
    game_id: u64,
}

#[get("/game/&lt;game_id&gt;")]
pub async fn view_game_info(
    game_id: i64,
    user: User,
    db: Connection
) -> Template {
    let game_data = fetch_game_data_from_somewhere();
    // Helper automatically adds the CSRF token into the template
+   TemplateWithCsrfToken::render("my_template", context! { game_data })
}

#[post("/game/&lt;game_id&gt;", data = "&lt;post&gt;")]
pub async fn update_game_ownership(
    game_id: i64,
    user: User,
    // This automatically validates the passed CSRF token
+   post: WebSessionCsrfProtectedForm&lt;MarkGameAsOwnedForm&gt;,
    db: Connection
) -> Template {
    Template::render("my_template", context! { whatever_data_here })
}
</code></pre>

As a reminder, this is *very close to* real production code (I just trimmed some of the details, and the HTML code changes are still omitted as in the last example). 

At first glance this doesn't seem all that different: sure, there's a few ergonomic types to wrap things in, but I still had to update 4 places, right? What's the security benefit? What if I forget to make these changes on the billing page?

And, well, so far, there isn't a security benefit. The library is just marked as a set of *ergonomic* helpers for CSRF protection, and it delivers on that.

## Enforcing security by default

To get the most out of [rocket_csrf_guard](https://github.com/mhlakhani/rocket_csrf_guard), you need to change your application code and development practices a little. The library helps, but isn't sufficient.

If you look at the definition of a CSRF attack [on the OWASP website](https://owasp.org/www-community/attacks/csrf) (emphasis mine):

> ... If the victim is a normal user, a successful CSRF attack can force the user to perform **state changing** requests like transferring funds, changing their email address, and so forth. ...

If we restate this a little - our goal is to make it impossible to run a state changing request that hasn't passed CSRF checks. And that's exactly what the [CsrfCheckProof](https://docs.rs/rocket_csrf_guard/latest/rocket_csrf_guard/enum.CsrfCheckProof.html) type is for. Whenever a CSRF check executes, the framework returns that (in the wrapper type, and in the request cache) and you can use that.

Concretely, I use this in [trackmy.games](https://trackmy.games) for all state changing operations with side effects. There's only 2 places where I do them (at least, accessible to external users):

* When sending emails (for account signup or password resets)
* Updating database records

Let's talk about securing the second. I built a homegrown library for database access (I hope to open source it at some later date, it's beneficial beyond just security) which splits out read versus write access. You can get a readonly connection very easily (similar to how rocket recommends it with e.g. [this library](https://crates.io/crates/rocket_sync_db_pools)). But you *cannot* get a connection that supports writes without passing a `CsrfCheckProof`. And that's all you need. Now, it doesn't matter if I am adding the new feature sleep-deprived at 2am or not, if I forget to wrap my form with CSRF protection using the steps laid out above, my code simply will not work at runtime. And we're secure!

For completeness' sake, here's how the `POST` route looks in my actual code:

<pre class="language-rust">
<code class="language-rust">
#[post("/game/&lt;game_id&gt;", data = "&lt;post&gt;")]
pub async fn update_game_ownership(
    game_id: i64,
    user: User,
    // This type first validates the incoming form's CSRF token
    // against the CSRF token in the user session, and then
    // opens a write connection to the DB by passing the proof to it
    post: WebSessionCsrfProtectedFormWithGuard&lt;
        '_,
        Form&lt;MarkGameAsOwnedForm&gt;,
        WriteConnection&lt;MyDbType&gt;,
    &gt;,
) -> Template {
    let (db, form) = post.into_parts();
    // Now use the database and the fields in the form...
    Template::render("my_template", context! { whatever_data_here })
}
</code></pre>

I made similar changes to `send_email` to just take a `CsrfCheckProof`. And that's it!

## Closing the loop

If you've gotten this far, congratulations! You know most of what's needed to write a secure framework to prevent security bugs. The main points are just:

* Clearly articulate what the root cause of the security problem is (in this case, state changing operations w/o CSRF checks)
* Make it impossible to do that (state changes require a proof of a CSRF check)

And that's it! If I was doing this in a larger company setting, I'd probably look into a couple more things. As written, if you make a mistake, the library will fail at runtime, when you actually try to exercise the code. Ideally it would be a compile time error (hard to do) or be paired up with a static analysis/lint warning - it should be possible, in theory, to write a check for cases when you write a `#[post]` route that uses a bare `Form` type and not one of the wrapped ones. Or I'd go and update `rocket` itself so requests get rejected earlier on/fail at route construction time. Or something... But that's for another time and another day.

## PS: Does the framework really do all of this?

Yes and no. Like I said, the focus here is on adding *ergonomic* wrappers so you can easily integrate CSRF protection into your Rocket application. It provides all the building blocks for that, but if you want the secure-by-default approach you'll have to do a little bit more work.

Aside from that, though, almost everything here is already available there (along with more features) - check out the [example app](https://github.com/mhlakhani/rocket_csrf_guard/blob/main/rocket_csrf_guard/examples/end_to_end.rs), which showcases what's possible. The code examples here really are pretty much taken from real code running in production - the only abstractions otherwise are:

* The User library (it's very similar to what's in the example app above though)
* The Database library (I'll open source that separately at some point...)
* The `TemplateWithCsrfToken` bit - this should be easy to clean up and add to `rocket_csrf_guard` if there is demand for it, in reality I have a few more fields I add on every template.

That's not to say the framework is done: There's a lot more stuff to be done to improve ergonomics (I'd love template library integration for example, so you don't have to update your HTML code), and I'm open to ideas and feedback.

### PPS: Isn't CSRF dead?

You might have seen posts like [this one](https://scotthelme.co.uk/csrf-is-really-dead/) talking about how CSRF is not a problem anymore. My response to that is two-fold:

* There are still cases where you can't use `SameSite=Strict` (we hit this due to the usage of browser extensions)
* And hey, I just needed an excuse to write about secure frameworks and this was a nice problem to discuss.

## TLDR

Taking a "professional" approach to security might be worth it even for side projects: it can save you time in the long run and avoid risk. And it's not too hard to do, depending on the problem you're trying to solve. Oh, and I wrote some code and a library to make your life easier, [please check it out](https://github.com/mhlakhani/rocket_csrf_guard).

As always, please let me know if you have any thoughts or feedback!