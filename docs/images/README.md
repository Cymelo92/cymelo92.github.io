# Profile image

The starter homepage currently loads the existing CALC Lab portrait from:

https://calclab.org/img/carlo-round.jpg

For a fully self-contained site, download that image (or another portrait you prefer) into this directory as:

carlo-round.jpg

Then change this line in `index.qmd`:

```markdown
![](https://calclab.org/img/carlo-round.jpg){.profile-photo fig-alt="Portrait of Carlo Y. Meloni"}
```

to:

```markdown
![](images/carlo-round.jpg){.profile-photo fig-alt="Portrait of Carlo Y. Meloni"}
```
