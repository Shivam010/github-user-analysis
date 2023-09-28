# github-user-analysis

Analyses candidate's Github contribution analysis using GCP's functions-framework-python

## Why move to Github Graphql API ?

When using Github Rest API, we will have to make too many calls to retrieve the information almost 30+ _(and that too when using the default page size limit, increasing the pagesize would have increases the calls even more)_.

This will result in much more consumption of Github's rate limit - `5000 requests per hour`, which means using Rest API we could only analyse `~150 users (=5000/30)` per hour.

But on using an efficient [Graphql query](./query.gql), we can obtained all the equivalent information in just a single call, which means the effectively, we can analyse `~5000` users per hour.

