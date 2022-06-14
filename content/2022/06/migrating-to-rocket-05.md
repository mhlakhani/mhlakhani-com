{
    "route": "post",
    "title": "Migrating from rocket 0.4 to 0.5",
    "date": "2022/06/14",
    "tags": ["rust", "rocket", "migration"],
    "excerpt": "Learn how to migrate your code to the new rocket version"
}


As alluded to in my [previous post](/blog/2022/06/software-maintenance-sucks/), I recently had to migrate my Rocket app (powering [https://reads.mhlakhani.com](https://reads.mhlakhani.com)) to v0.5 so it could keep compiling. This was a major version bump with a lot of breaking changes, so there was a lot to fix. Thankfully it took just a few days instead of a few weeks so the site is back up sooner than expected. This post documents what I had to do in case it helps anyone else.

For reference, the final diff was "18 changed files with 1841 additions and 1803 deletions", though about half of that was generated changes in `Cargo.lock`.

## A primer

[Rocket](https://rocket.rs/) is a (IMO, excellent) web framework for Rust that has a lot of bells and whistles - it lets you be productive and quickly get your job done without getting in the way. I've used it to power a few of my sites for a long time.

Until recently, it did not support async, and only compiled on Rust nightly. That's all fixed as of the new and upcoming 0.5 version, which is a massive overhaul of the framework and associated libraries. I'd been planning on migrating for a while, but kept putting it off. After migrating my server and upgrading the Rust compiler though, I could no longer put it off as the latest nightly compiler doesn't accept the code anymore.

How bad could it get? I pulled out the [migration guide](https://rocket.rs/v0.5-rc/guide/upgrading-from-0.4/#upgrading) and read the [changelog](https://github.com/SergioBenitez/Rocket/blob/v0.5-rc/CHANGELOG.md) and got to work. After updating the dependencies in `Cargo.toml` for `rocket` and `rocket_sync_db_pools`, I tried to compile, and ... I got 100s of compiler errors. This was quite overwhelming. I was about to give up till [I found this example](https://github.com/ZeusWPI/zauth/pull/80/files) and realized it might not be as bad as I feared.

To limit the scope of the problem, I commented out most of the code, leaving in the basics: the database access code (I use `diesel`), a few simple routes that would exercise templating (using `askama`) and state access, and the main set up code. That still had ~100 errors, but it was more manageable now. Off to the races.

## Database access

First off, `rocket_contrib` was no longer a thing so I had to find another solution for database access. The guide suggested moving to `rocket_sync_db_pools`. This was mostly straightforward. In my database code I had to make a couple of changes to set up the db:

<pre class="language-diff-rust diff-highlight">
<code class="language-diff-rust diff-highlight">
-use rocket_contrib::databases;
+use rocket_sync_db_pools::database;
...
-#[rocket_contrib::database("mhlrds_db")]
-pub struct DbConn(databases::diesel::SqliteConnection);
+#[database("mhlrds_db")]
+pub struct DbConn(pub diesel::SqliteConnection);</code></pre>

The query interface also changed now, however, since it's now async (sorta -- diesel is still sync, so the async wrapper eventually goes to a thread pool). All the queries had to change as a result:

<pre class="language-diff-rust diff-highlight">
<code class="language-diff-rust diff-highlight">
-diesel::replace_into(facebook_graphapi_post::table)
-    .values(&to_insert)
-    .execute(connection)?;
+connection
+    .run(move |connection| {
+        diesel::replace_into(facebook_graphapi_post::table)
+            .values(&to_insert)
+            .execute(connection)
+    })
+    .await?;</code></pre>

## Templating

I used `askama` as it provides fast (templates are baked in at compile time), type safe templating. There is no stable new release that supports Rocket 0.5, but [this reply](https://github.com/djc/askama/issues/524?#issuecomment-1110382504) pointed to a version I was able to use. Everything still worked after that, aside from a couple of places where I had to replace an `.as_ref()` with a `.clone()` to satisfy the borrow checker.

## URL Routing

Rocket now boasts an enhanced `uri!` macro which is type safe. This actually caught a few bugs in my code. The migration was fairly straightforward, but I had to adjust dozens of callsites, mostly mechanically:

<pre class="language-diff-rust diff-highlight">
<code class="language-diff-rust diff-highlight">
-Ok(Redirect::to(uri!(archives: year = year, month = month,)))
+Ok(Redirect::to(uri!(archives(year = year, month = month))))</code></pre>

## Changes to route functions

Route functions now support async, so I went ahead and swapped out all of them to be async, and started using `.await` everywhere they called the (now) async db functions.

State extraction was also changed, so I had to replace all arguments of the form `State<T>` with `&State<T>` - thankfully this was a straightforward find/replace.

### Forms and (nested) forms

Routes need input! Thankfully almost none of the code had to change, [despite forms being revamped](https://rocket.rs/v0.5-rc/guide/upgrading-from-0.4/#forms).

There was one form I had to change, as I'd implicitly used [nesting](https://rocket.rs/v0.5-rc/guide/requests/#nesting) before:

<pre class="language-diff-rust diff-highlight">
<code class="language-diff-rust diff-highlight">
-#[derive(Debug, FromForm)]
-pub struct WebhookVerificationForm {
-    #[form(field = "hub.mode")]
-    mode: String,
-    #[form(field = "hub.verify_token")]
-    token: String,
-    #[form(field = "hub.challenge")]
-    challenge: String,
-}
+struct Hub&lt;'r&gt; {
+    mode: &'r str,
+    verify_token: &'r str,
+    challenge: &'r str,
+}
+
+#[derive(Debug, FromForm)]
+pub struct WebhookVerificationForm&lt;'r&gt; {
+    #[field(name = "hub")]
+    hub: Hub&lt;'r&gt;,
+}</code></pre>

The route code also had to change very slightly, accepting a `WebhookVerificationForm<'_>` instead of a `Form<WebhookVerificationForm>`.

### Errors

While the *inputs* to routes didn't change, the outputs did. I was previously returning `failure::Error` and Rocket would automatically return an error page. This no longer worked as the type did not implement `Responder`.

Since the app was a few years old, I decided to just rip it out and move to `anyhow` and `thiserror` by defining a custom error type.

This had a bunch of benefits across the code, most notably that I could now more easily do `?` everywhere and remove a bunch of `map_err` calls. The main change here was to change a few imports, and replace `format_err!(...)` with `anyhow!(...).into()` across the codebase.

Implementing `Responder` was a little tricky, but I copied [this solution](https://stuarth.github.io/rocket-error-handling) and it worked like a charm!

## Async mutexes

Now that everything is async, I realized I needed to move to using `tokio`'s async mutexes instead of regular mutexes, to avoid deadlocks and slowdowns. Mutexes were rare in my app, but they were needed for a few state objects that were shared across requests.

The changes were mostly like this:

<pre class="language-diff-rust diff-highlight" style="margin-inline-end: -10em">
<code class="language-diff-rust diff-highlight">
-use std::sync::Mutex;
+use tokio::sync::Mutex;
...
-pub fn sync_reindex(&self, connection: &SqliteConnection) -&gt; Result&lt;(), Error&gt {
-    let posts = Self::fetch_posts(connection)?;
-    let search = Search::new(posts)?;
-    *state.lock().unwrap() = Some(search);
-    Ok(())
-}
+pub async fn reindex(&self, connection: &DbConn) -&gt; Result&lt;(), Error&gt; {
+    let posts = Self::fetch_posts(connection).await?;
+    // This is expensive and CPU bound so spawn something in the background
+    let search = tokio::task::spawn_blocking(|| Search::new(posts)).await??;
+    *self.search.lock().await = Some(search);
+    Ok(())
+}</code></pre>

## Utilizing async

That wasn't enough - I could also optimize some of my code now! I was using `reqwest` to send HTTP requests to upstream. Since Rocket wasn't async previously, I had to manage my own tokio runtime and spawn it before sending requests, which wasn't great.

This code could all be cleaned up:

<pre class="language-diff-rust diff-highlight" style="margin-inline-end: -10em">
<code class="language-diff-rust diff-highlight">
-pub fn refetch_single_post(id: &str, conn: &SqliteConnection) -> ... {
-    let mut tokio = Runtime::new()?;
-    let response = tokio.block_on(reqwest::get(&url))?;
-    if response.status().is_success() {
-        let data: serde_json::Value = tokio.block_on(response.json())?;
-    // ... trimmed
-}
+pub async fn refetch_single_post(id: &str, conn: DbConn) -> ... {
+    let response = reqwest::get(&url).await?
+    if response.status().is_success() {
+        let data: serde_json::Value = response.json().await?;
+    // ... trimmed
+}
</code></pre>

## Config management

I have a global configuration singleton that reads the rocket config and sets up a `State` that routes can use (for things like app secrets, admin IDs, etc). This was previously implemented as a fairing that set itself up during `on_attach` by getting the config as follows:

<pre class="language-rust">
<code class="language-rust">
fn on_attach(&self, rocket: Rocket) -&gt; Result&lt;Rocket, Rocket&gt; {
    let app_id = rocket.config.get_string("external_app_id")?;
    // etc
    Ok(rocket.manage(Config{app_id, ...}))
}</code></pre>

The config management [has been revamped](https://rocket.rs/v0.5-rc/guide/upgrading-from-0.4/#configuration) and so this code needed to change too.

This became much easier now - just define a struct with your fields that implements `Deserialize`, and extract it:

<pre class="language-rust" style="margin-inline-end: -10em">
<code class="language-rust">
#[derive(Debug, Deserialize)]
struct BaseConfig {
    app_id: String,
    // other fields
}
pub struct Config {
    inner: Arc&lt;Mutex&lt;RefCell&lt;BaseConfig&gt;&gt;&gt;,
}
impl Config {
    pub fn configure(&self, rocket: &Rocket&lt;Orbit&gt;) -&gt; Result&lt;(), Error&gt; {
        let inner: BaseConfig = rocket.figment().extract()?;
        *self.inner.lock().unwrap() = RefCell::new(inner);
        Ok(())
    }
}</code></pre>

Note that I don't use an async mutex here, just a regular one - this is only written to on startup and the lock is never held across await points.

This code needed to be invoked differently though - I'll touch on that in the initialization section later.

## Authentication

Following the recommendations on the [rocket guide](https://rocket.rs/v0.5-rc/guide/requests/#forwarding-guards), I have an `AdminUser` implemented as a request guard. The type signature, and the mechanism to access cookies changed a little, but it was fairly minor:

<pre class="language-diff-rust diff-highlight" style="margin-inline-end: -15em">
<code class="language-diff-rust diff-highlight">
-impl&lt;'a, 'r&gt; FromRequest&lt;'a, 'r&gt; for AdminUser {
+#[rocket::async_trait]
+impl&lt;'r&gt; FromRequest&lt;'r&gt; for AdminUser {
    type Error = ();

-    fn from_request(request: &'a Request&lt;'r&gt;) -&gt; request::Outcome&lt;AdminUser, ()&gt; {
-        let config = request.guard::&lt;State&lt;Config&gt;&gt;()?;
-        let cookies = request.guard::&lt;Cookies&lt;'_&gt;&gt;();
-        if let Some(mut cookies) = cookies.succeeded() {
+    async fn from_request(request: &'r Request&lt;'_&gt;) -&gt; request::Outcome&lt;AdminUser, ()&gt; {
+        let config = request.guard::&lt;&State&lt;Config&gt;&gt;().await;
+        if let Some(config) = config.succeeded() {
+            let cookies = request.cookies();
             if let Some(cookie) = cookies.get_private(COOKIE_NAME) {
             // As before...
...
-pub fn login_post(
-    config: State&lt;Config&gt;,
-    mut cookies: Cookies,
+pub async fn login_post(
+    config: &State&lt;Config&gt;,
+    cookies: &CookieJar&lt;'_&gt;,</code></pre>

## Initialization

Rocket now comes with its own helper macros to help with initialization and running. Your main function can get quite simplified if you replace it with a function annotated with the `launch` macro, and just return a `Rocket`. That's what I did:

<pre class="language-diff-rust diff-highlight">
<code class="language-diff-rust diff-highlight">
-fn main() {
-    let runner = rocket::ignite()
-        .attach(...)
-        .mount(...)
-        // More routes, states, and initialization code ...
-    runner.launch();
-}
+#[launch]
+async fn run() -> Rocket<Build> {
+    rocket::build()
+        .attach(...)
+        .mount(...)
+        // More routes and states...
+}</code></pre>

This wasn't sufficient for my needs though. I had some custom initialization for e.g. migrations and state types which needed access to both the `Rocket` object and a DB connection. This had to change a little:

<pre class="language-diff-rust diff-highlight" style="margin-inline-end: -5em">
<code class="language-diff-rust diff-highlight">
-let connection = db::DbConn::get_one(&runner);
-if let Some(connection) = connection {
-    let paginator: Option&lt;
-        State&lt;ReadingListPaginator&gt;,
-    &gt; = State::from(&runner);
-    paginator
-        .expect("Error fetching paginator!")
-        .sync_reindex(&connection)
-        .expect("Error initializing paginator!");
+.attach(AdHoc::on_liftoff(
+    "ReadingListPaginator initializer",
+    |rocket| {
+        Box::pin(async move {
+            let connection = db::DbConn::get_one(rocket)
+                .await
+                .expect("couldn't get DB connection!");
+            let paginator: Option&lt;&State&lt;ReadingListPaginator&gt;&gt; =
+                State::get(rocket);
+            paginator
+                .expect("Error fetching paginator!")
+                .deref()
+                .reindex(&connection)
+                .await
+                .expect("Error computing pagination!");
+        })
+    },
+))
</code></pre>


I wish Rocket had something better for this pattern (so you didn't have to first attach an empty state and then initialize it later), and I'm open to ideas!

## The losses

I did have to give up one feature - prometheus metrics. As far as I can tell, the library does not support rocket 0.5 yet. I wasn't using them too much though, so it was a tiny change to remove support.

## Conclusion

Migrating from Rocket 0.4 to 0.5 can seem overwhelming at first, but it's doable as most of the changes follow fairly straightforward pattens. This post hopefully covers a few major types of changes you may have to make to smoothen the transition. A lot of minor details (such as switching imports for types that moved from one module to another) were left out, but this covered about 95% of what I had to do.

Please let me know if you found this useful!