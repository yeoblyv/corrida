# notebooks/

Jupyter notebooks, for three specific jobs — see
[CONTRIBUTING.md §7](../CONTRIBUTING.md#7-notebooks) for the full rules.
Create the subfolder when you add its first notebook; none are
pre-created here.

```
notebooks/
├── demos/          finished, outputs kept on purpose - point the report/presentation here
├── exploration/     working out something labor-intensive before it's real code in src/
└── cheatsheets/      runnable reference notes, same spirit as docs/git-cheatsheet.md
```

A notebook is never the only copy of logic that runs on the robot -
that always lives in `src/`, tested per
[CONTRIBUTING.md §6](../CONTRIBUTING.md#6-tests).
