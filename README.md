### Buy New

online shopping platform

### Frontend development

The Vue frontend is served by Frappe from `buy_new/public/frontend`. Run the
bench processes with `bench start`; its `frontend` process builds the Vue app
and watches for changes. After editing a Vue file, refresh the page to load the
new bundle. Python changes are reloaded by Frappe's development server.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app buy_new
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/buy_new
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
