# w2g

The World Wide Graph

## Purpose

The World Wide Graph (w2g) aims to become a global database of unique entities (people, places, things) which is accessible by the entire World Wide Web. It aims to aggregate and entity resolve existing entity graph services, like Wikidata, Freebase, Google Knowledge Graph, the Facebook Graph, as well as provides its own database (for creating new entities which don't align with these services -- e.g. Wikidata doesn't allow "unnotable" names of people -- or for when one of these services is read only and needs to be extended).

A neat property of w2g is, it's more than an raw entity database which unites existing services. w2g has the ability to create directed `edges` between entities and arbitrary `contexts` (think of them like isolated groups of edges you can control / restrict to your application or preferences). For instance, one can establish a `context` of `Inventions` whose intent is to create a dependency graph which demonstrates how to axiomatically build an invention. One can then establish an edge between and entity `Electric Generator` and `Magnet`.

## Data Structures

- `contexts` are named semantic groups (name comes from the entity it represents) under which a set of `edges` are applicable. For instance, an `edge` representing the entity (property) `derivation` may be created between and entity named `Rational` and an entity named `Ratio` within the context of the entity `Etymology`. However, consider someone else may be instead instead in comparing the relationship of these entities as mathematical terms.
- `edges` are directed relationships (often dependencies) between two entities. Edges themselves can be associated with / represent an entity (have a relation_eid).

## Goals

- **Interoperability.** To allow any website to connect to the Graph and resolve/render terms against semantic elements. This is done in a way which is very similar to wikidata's [qlabel](http://googleknowledge.github.io/qlabel).
- Pub/sub scribe to tags and get notified when your (personal) entity is `@mentioned`.

## Philosophy

W2g will work similarly to Wikipedia + Wikidata. Anyone can suggest edits or register nodes, permitting they provide adequate proof. Some imaginary w2g committee will reviews each case for quality and accuracy. 

Want to be on the committee? Email michael.karpeles@gmail.com to help

## Privacy & Conflicts of Interest

W2g is an open source, non-profit initiative. I'm mostly building it as a convenient programatic interface for establishing dependency graphs between entities which already exist on disprate remote services. 

## Using the Graph

Any website in the world can tap into the global graph (CORs is enabled on the API). Doing so is as easy as importing a single javascript library, just like google analytics. Spoiler: The javascript library [graph.js](https://github.com/w2g/graph.js) doesn't exactly exist yet but it will be (optionally) served via some cdn, such as:

    <script type="text/javascript" src="https://graph.global/static/assets/graph.js"></script>

By including graph.js in your website, any html tag which references a w2g entity will be resolved and rendered as a w2g tag (additionally with correct schema.org markup). By default, a tag has minimal style, like a link / anchor tag. It is distincly colored (green, instead of blue) and italicized by the cite tag (instead of underlined)
