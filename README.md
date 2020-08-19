# Permapol

[![Docker Repository on Quay](https://quay.io/repository/genouest/permapol/status "Docker Repository on Quay")](https://quay.io/repository/genouest/permapol)

Permission manager for Apollo

## Required env variables

* APOLLO_URL *Url to the apollo API*
* APOLLO_USER *Apollo admin user*
* APOLLO_PASSWORD *Apollo admin password*

## Optional env variables

* PROXY_HEADER *Default to REMOTE_USER*
* USER_AUTOCOMPLETE *Default to FALSE. If set to TRUE, there will be an autocompletion when adding user to a group*
* CRON_SYNC *Default to FALSE. If set to TRUE, a cron will run daily to remove access to an organism if the admin lost access*
