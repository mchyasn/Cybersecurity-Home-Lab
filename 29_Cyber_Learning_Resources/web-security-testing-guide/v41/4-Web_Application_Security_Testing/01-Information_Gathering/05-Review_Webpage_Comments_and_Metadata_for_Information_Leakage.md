---

layout: col-document
title: WSTG - v4.1
tags: WSTG

---
# Review Webpage Comments and Metadata for Information Leakage

|ID           |
|-------------|
|WSTG-INFO-05|

## Summary

It is very common, and even recommended, for programmers to include detailed comments and metadata on their source code. However, comments and metadata included into the HTML code might reveal internal information that should not be available to potential attackers. Comments and metadata review should be done in order to determine if any information is being leaked.

## Test Objectives

Review webpage comments and metadata to better understand the application and to find any information leakage.

## How to Test

HTML comments are often used by the developers to include debugging information about the application. Sometimes they forget about the comments and they leave them on in production. Testers should look for HTML comments which start with " ".

### Black-Box Testing

Check HTML source code for comments containing sensitive information that can help the attacker gain more insight about the application. It might be SQL code, usernames and passwords, internal IP addresses, or debugging information.

```html
...

<div class="table2">
  <div class="col1">1</div><div class="col2">Mary</div>
  <div class="col1">2</div><div class="col2">Peter</div>
  <div class="col1">3</div><div class="col2">Joe</div>

<!-- Query: SELECT id, name FROM app.users WHERE active='1' -->

</div>
...
```

The tester may even find something like this:

```html
<!-- Use the DB administrator password for testing:  f@keP@a$$w0rD -->
```

Check HTML version information for valid version numbers and Data Type Definition (DTD) URLs

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
```

- `strict.dtd` -- default strict DTD
- `loose.dtd` -- loose DTD
- `frameset.dtd` -- DTD for frameset documents

Some Meta tags do not provide active attack vectors but instead allow an attacker to profile an application to

```html
<META name="Author" content="Andrew Muller">
```

A common (but not WCAG compliant) Meta tag is the refresh.

```html
<META http-equiv="Refresh" content="15;URL=https://www.owasp.org/index.html">
```

A common use for Meta tag is to specify keywords that a search engine may use to improve the quality of search results.

```html
<META name="keywords" lang="en-us" content="OWASP, security, sunshine, lollipops">
```

Although most web servers manage search engine indexing via the robots.txt file, it can also be managed by Meta tags. The tag below will advise robots to not index and not follow links on the HTML page containing the tag.

```html
<META name="robots" content="none">` `
```

The Platform for Internet Content Selection (PICS) and Protocol for Web Description Resources (POWDER) provide infrastructure for associating meta data with Internet content.

### Gray-Box Testing

Not applicable.

## Tools

- [Wget](https://www.gnu.org/software/wget/wget.html)
- Browser “view source” function
- Eyeballs
- [Curl](https://curl.haxx.se/)

## References

### Whitepapers

- [HTML version 4.01](https://www.w3.org/TR/1999/REC-html401-19991224)
- [XHTML](https://www.w3.org/TR/2010/REC-xhtml-basic-20101123/)
- [HTML version 5](https://www.w3.org/TR/html5/)
