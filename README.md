# gustavo.jasso.info - a mathematician's simple website

This website is built using [Hugo](https://gohugo.io/) according to my own personal needs, which are minimal: indicate institutional affiliation through simple design elements, simple navigation and simple maintenance.

* [Install Hugo](https://gohugo.io/installation/)

* [Install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

Follow the following steps for cloning this repository and building this website locally in your computer. 

```
$ git clone git@git.sr.ht:~gjasso/gustavo.jasso.info
$ cd gustavo.jasso.info
$ hugo
```

Hugo will generate the website and store it in the `public` directory that can then be published. 

If you wish to modify this website for your personal use, you will want to modify (at least) the following files:

```
config.toml
content/_index.md
layouts/partials/footer.html
```

The [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) stylesheet is stored under `static/css/`. The photograph and LU's logotype are stored under `static/img/`.

The following guide might be useful if you are unfamiliar with Hugo:

[Get started with Hugo](https://gohugo.io/getting-started/quick-start/**

**TODO** Automation through datasets and BibTeX import(s).
