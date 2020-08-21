# Permapol

[![Docker Repository on Quay](https://quay.io/repository/genouest/permapol/status "Docker Repository on Quay")](https://quay.io/repository/genouest/permapol) ![Lint](https://github.com/genouest/permapol/workflows/Lint/badge.svg)

A permission manager for Apollo, designed to ease collaboration when coupled with a Galaxy instance.

Users can freely create user groups, and grant them access to the organisms they create from Galaxy. No admin rights need to be granted to anyone for this, allowing more autonomy while staying as secure as possible.

The Web UI is exposed on port 80 by default.

Authentication is based on a REMOTE_USER header that should be set by a reverse proxy properly configured (like nginx with ldap auth).

## Running with docker-compose

A typical docker-compose.yml to run this app looks like that:

```
version: '3.7'
  services:

    permapol:
    	image: quay.io/genouest/permapol
            environment:
                APOLLO_URL: "http://apollo"
                APOLLO_USER: "admin@apollo.com"
                APOLLO_PASSWORD: "xxxxxxx"
```

## Required env variables

* APOLLO_URL *Url to the apollo API*
* APOLLO_USER *Apollo admin user*
* APOLLO_PASSWORD *Apollo admin password*

## Optional env variables

* PROXY_HEADER *Default to REMOTE_USER*
* PROXY_PREFIX *Default to None. This is the url prefix set py the proxy.
* USER_AUTOCOMPLETE *Default to FALSE. If set to TRUE, there will be an autocompletion when adding user to a group*
* CRON_SYNC *Default to FALSE. If set to TRUE, a cron will run daily to remove access to an organism if the admin lost access*
