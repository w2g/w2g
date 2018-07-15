# w2g

The World Wide Graph: A simple, collaborative, semantic graph database for the entire web to share.

* [Introduction](#gentle-introduction)
* [Limitations of the Web](#limitations-of-the-web)
* [Installing w2g (Server)](#getting-started)
* [Goals & Philosophy](#goals--philosophy)
* [Data Structures](#data-structures)
* [Privacy, Security & Conflicts of Interest](#privacy-security--conflicts-of-interest)
* [Using the Graph API (Clients)](#consuming-the-graph)

## Introduction

**A Simple Shared Knowledge-Base for the Web**. The World Wide Graph (w2g) aims to become a global, collaborative (wiki-like), semantic graph database of unique entities (people, places, events, things), like Wikidata, which is accessible and can be written to and read from by any person or page on the world wide web. 

It aims to aggregate and entity resolve entities from/across existing graph / knowledge-base services, like Wikidata, Freebase, Google Knowledge Graph, Facebook Open Graph, as well as provides its own database (for creating new entities which don't align with these services -- e.g. Wikidata doesn't allow "unnotable" names of people -- or for when one of these services is read only and needs to be extended).

## Limitations of the Web

A limitation of the World Wide Web is that each website operates independently within their own little silos. Data on one website can't be easily accessed by another website except through fragile, bespoke (rest) APIs. Connecting one website to another isn't automatic and often requires separate integration for each additional website or service which is to be attached.

Once and a while, a platform like Wikipedia or Facebook will come along and pioneers their own layer on top of the world wide web, adding essential functionality and/or novel structure. In a sense, its almost as if they are creating their own web-within-a-web: their own separate version of the web wherein enhancements are made possible across all their pages but not to other websites beyond their domain. For Facebook and Twitter, this might manifest as the novel ability to auto-complete and tag your friends in order to associate them with or alert them of content. Twitter and Facebook each have their own database of tags which are only relevant within their own respective services. You cannot tag people across services. This results in users ending up with numerous, fragmented identities across facebook, twitter, github, and all their other online presences. Wikipedia may provide a structured playground with millions of articles, but imagine how much more useful it would be if everyone in the world could tag content in their website as being related to a wikipedia topic, and you could query across all of them -- adding every site on the web to a global conversation.

W2g offers this with an alternative approach, where a common, public/open database with a well defined interface, is made available to website which wishes to attach and read or contribute knowledge.

There doesn't need to be just one w2g -- in fact, there probably shouldn't be. Different interoperable World Wide Graphs could and should emerge to serve different communities and needs.

### Why not just use Wikidata?

Wikidata is a perfect example of a project which could use a w2g (not that I'm recommending they do). The point of w2g is to white-label the functionality of Wikidata and make it as light-weight and as simple/easy as possible for others to adapt for their own use cases. There should be many systems like Wikidata. And they should all enforce their own guidelines and rules for quality, but most importantly, they should be designed to interoperate with each other as a first principle.

In fact, there already are several systems like Wikidata in existence today. Google has their own Knowledge Graph. Facebook has its Open Graph. And few of these systems are designed to allow a user to query across systems.

Most of these systems aren't open. That means, the data requires special privileged keys to access. Wikidata is open but it has notability policies which make it difficult for people to use it for anything other than the Wikidata community decides. The platform which runs Wikidata could be repurposed and white-labeled (in almost an identical fashion as w2g is trying to achieve), but the code-base is so sufficiently complex, that it seemed prudent to start with a simple, minimalist prototype that anyone could easily get up and running and adapt to their needs. Wikidata provides a bunch of functionality which is beyond the scope of the core value propositions w2g hopes to highlight, and I'd hate for its mission to be drowned out by Wikidata's added complexity.

## Inspiration

This project is inspired by Freebase & Wikidata, [Ted Nelson's ZigZag](http://xanadu.com/zigzag), Facebook & twitter semantic tags, and most importantly, the Memex as described within [Vannevar Bush's, "As We May Think"](https://www.theatlantic.com/magazine/archive/1945/07/as-we-may-think/303881/). For additional context, consider reading [Alex Wright's, "GLUT: Mastering Information Through the Ages"]. W2g (while independently conceived) is almost synonymous with Tim Berners-Lee's [Giant Global Graph](https://en.wikipedia.org/wiki/Giant_Global_Graph).

## Goals & Philosophy

Openness. Collaboration. Interoperability. Persistence. Decentralization. Universal Identity. Deduplication. 

- **Interoperability.** To allow any website to connect to the Graph and resolve/render terms against semantic elements. This is done in a way which is very similar to wikidata's [qlabel](http://googleknowledge.github.io/qlabel).
- Pub/sub scribe to tags and get notified when your (personal) entity is `@mentioned`.

https://graph.global is my pilot instance of w2G and I imagine it could work similarly to Wikipedia + Wikidata.
Many interoperable w2gs may emerge and run in parallel which each serve unique community needs.

## Get Involved

Want to be on the committee? Email michael.karpeles@gmail.com to help

## Privacy, Security & Conflicts of Interest

W2g is an open source, non-profit initiative. I'm mostly building it as a convenient programatic interface for establishing dependency graphs between entities which already exist on disprate remote services. 

# Developers Guide

## Getting Started

### Prerequisites

* **Python.** w2g requires python2.7 or python3.4. Note: there are some features (e.g. the /admin sqlalchemy CMS interface -- 2.7 only) which have dependencies which are only available for either 2.7 or 3.4.
* **Postgresql 9.4** e.g. postgresql-9.4 postgresql-server-dev-9.4 (aptitude)

### Installation

    $ git clone https://github.com/w2g/w2g.git
    $ cd w2g
    $ ./install.sh  # for ubuntu / debian system pre-requisite dependencies (like psql) 
    $ pip install .  # for python lib dependencies 

### Setting up the DB

First, create a user and a database for the project to use:

    $ sudo -u postgres psql
    postgres=# create user w2g with password 'yourPasswordHere' login createdb;
    postgres=# create database w2g owner w2g;
    
Next, create a file called `settings.cfg` with the following contents within `w2g/configs/`. Replace `yourPasswordHere` with the value you choose when creating your pql database. Under the `[security]` section, fill in a value for `secret = ` by generating os.urandom(24) -- see: http://flask.pocoo.org/docs/0.10/quickstart/#sessions "How to generate good secret keys":

    [server]
    host = 0.0.0.0
    port = 8080
    debug = 1
    cors = 1
    
    [security]
    secret = 
    
    [db]
    user = w2g
    pw = yourPasswordHere

#### Loading sql data from a dump (Coming soon)

I am attempting to setup an endpoint https://graph.global/v1/db to download/stream a sql dump of the production database (so people can back it up or easily achieve a dump).

#### Creating an Tables

Once your database and user have been created, and the user has the correct permissions, run the following:

    $ cd w2g
    $ ls  # confirm you're in the package root
    api/ app.py configs/ ...
    $ python
    >>> import api
    >>> api.core.Base.metadata.create_all(api.engine)  # creates tables from sqlalchemy models in api.graph.py

### Run w2g server

    $ python app.py
    * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)

## Data Structures

-- **`entities`**: primitives of the system; generally people, places, things, actions, thoughts, categorizations, or relational descriptors (like `friends with`).

- **`edges`** are directed relationships (often dependencies) between two `entities`. Edges themselves can be associated with / represent an entity (have a relation_eid). Basically, think RDF triples.

- **`contexts`**: w2g plans on adding the ability to add any number of `context` tag(s) to `relation`s. e.g. It may be important to you that `Mek` <> `friends with` <> `Drew` only matters within the `context` of `Mek's Friends` and someone else may want to ignore these queries if we're sharing the same global graph. You can think of `context`s like isolated groups of edges you can control / restrict to your application or preferences. For instance, one can establish a `context` of `Inventions` whose intent is to create a dependency graph which demonstrates how to axiomatically build an invention. One can then establish an edge between and entity `Electric Generator` and `Magnet`. Thought of another way, `contexts` are named semantic groups (name comes from the entity it represents) under which a set of `edges` are applicable. For instance, an `edge` representing the entity (property) `derivation` may be created between and entity named `Rational` and an entity named `Ratio` within the context of the entity `Etymology`. However, consider someone else may be instead instead in comparing the relationship of these entities as mathematical terms.

## Green Text

No, not like 4chan's "greentext". W2g `green text` is how w2g `entities` (semantic tags) are rendered and represented in the browser. They can be right clicked in order to navigate to their definitions. 

The World Wide Web Consortium (W3C) is the de facto international working group responsible for developing Web standards. They work with stakeholders and arrive at agreements, such as a hypertext link should be blue and underlined and then become purple after its visited.

W2g isn't so fancy as to be anything worth acknowledging by the W3C (we'd be lucky to make it into the W2C -- which is a fictional thing with one less "W" that doesn't exist; I'm making a joke. Ha ha) however, w2g similary share the belief that working together, participating in thoughtful public discussion, and documenting standards are useful and important practices. And so it is with this spirit that w2g proposes its own minimal set of primitives, which are hopefully compatible with and complimentary to the W3C's existing standards.

The fundamental primitive of w2g is the `<cite>` tag. `<cite>` was chosen because it doesn't have any pre-existing default functionality (e.g. whereas a link is clickable). It adds consistent semantic value, in that an entity is being cited within the tag. It can be combined with, but avoids conflating itself with an `<a>` anchor tag. It adds to an existing w3c tag without trying to introduce an entirely new foreign primitive.

A w2g `<cite>` tag identifies/distinguishes itself in css by have a `w2gid` property -- i.e. `cite[w2gid]`. Within HTML, this looks something like `<cite w2gid="123">`. w2g `<cite>` tags are given a few affordances beyond how the browser generally renders them. A `w2g <cite>` tag has minimal style whose emphasis is intended to be consistent to that of an anchor tag. It is distincly colored (green #008000, instead of blue #0000ff) and italicized by the cite tag (instead of underlined).

Finally, and most controversially, a w2g `cite[w2gid]` instance is invoked via the "right click" action or a long hold. This functionality can alternatively be achieved, if desired, on desktop through `:hover`ing. When clicked, a `cite[w2gid]` tag will bring the user to https://graph.global/?id=XXX (or some other w2g instance) where `XXX` is the `w2gid` property value. 


## Consuming the Graph

Any website in the world can tap into the global graph (CORs is enabled on the API). Doing so is as easy as importing a single javascript library, just like google analytics. Spoiler: The javascript library [graph.js](https://github.com/w2g/graph.js) doesn't exactly exist yet but it will be (optionally) served via some cdn, such as:

    <script type="text/javascript" src="https://graph.global/static/assets/graph.js"></script>

By including graph.js in your website, any html tag which references a w2g entity will be resolved and rendered as a w2g tag (additionally with correct schema.org markup). By default, a tag has minimal style, like a link / anchor tag. It is distincly colored (green, instead of blue) and italicized by the cite tag (instead of underlined)


