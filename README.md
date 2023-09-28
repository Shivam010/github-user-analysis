# github-user-analysis

Analyses candidate's Github contribution analysis using GCP's functions-framework-python

## Why move to Github Graphql API ?

When using Github Rest API, we will have to make too many calls to retrieve the information almost 30+ _(and that too when using the default page size limit, increasing the pagesize would have increases the calls even more)_.

This will result in much more consumption of Github's rate limit - `5000 requests per hour`, which means using Rest API we could only analyse `~150 users (=5000/30)` per hour.

But on using an efficient [Graphql query](./query.gql), we can obtained all the equivalent information in just a single call, which means the effectively, we can analyse `~5000` users per hour.

## Sample example

```json
{
	"data": {
		"name": "Shivam Rathore",
		"twitterUsername": "010Shivam",
		"username": "Shivam010",

		"createdAt": "2017-05-30T17:57:25Z",
		"updatedAt": "2023-09-26T21:08:04Z",
		"location": "India",

		"followers": 44,
		"following": 57,

		"bio": "Software Developer 🚀",
		"socialAccounts": [
			{
				"displayName": "@010Shivam",
				"provider": "TWITTER",
				"url": "https://twitter.com/010Shivam"
			},
			{
				"displayName": "in/shivam010",
				"provider": "LINKEDIN",
				"url": "https://www.linkedin.com/in/shivam010/"
			},
			{
				"displayName": "https://medium.com/@Shivam010",
				"provider": "GENERIC",
				"url": "https://medium.com/@Shivam010"
			}
		],

		"isDeveloperProgramMember": false,

		"totalRepositories": 62,
		"totalStarredRepositories": 450,
		"totalStarsReceived": 527,

		"hasSponsorsListing": true,
		"totalSponsors": 0,
		"totalSponsorings": 0,
		"totalSponsorshipAmountAsSponsorInCents": null,
        
		"oneYearContributionsStats": {
			"hasAnyContributions": true,
			"popularIssueContribution": {},
			"popularPullRequestContribution": {},
			"restrictedContributionsCount": 1062,
			"timePeriod": {
				"endedAt": "2023-09-29T03:59:59Z",
				"startedAt": "2022-09-25T04:00:00Z"
			},
			"totalCommitContributions": 33,
			"totalIssueContributions": 2,
			"totalPullRequestContributions": 2,
			"totalPullRequestReviewContributions": 4,
			"totalRepositoriesWithContributedCommits": 9,
			"totalRepositoriesWithContributedIssues": 2,
			"totalRepositoriesWithContributedPullRequestReviews": 2,
			"totalRepositoriesWithContributedPullRequests": 2,
			"totalRepositoryContributions": 3
		},
        
		"recentlyContributedRepositories": [
			{
				"forkCount": 48,
				"langauges": [
					{
						"name": "Go",
						"size": 90659
					},
					{
						"name": "Shell",
						"size": 301
					}
				],
				"primaryLanguage": {
					"name": "Go",
					"size": 90659
				},
				"stargazerCount": 328,
				"url": "https://github.com/nitishm/go-rejson"
			}
			// ... other
		],
        
		"topRepositories": [
			{
				"forkCount": 0,
				"langauges": [
					{
						"name": "TypeScript",
						"size": 22982
					},
					{
						"name": "JavaScript",
						"size": 18599
					},
					{
						"name": "CSS",
						"size": 1748
					}
				],
				"primaryLanguage": {
					"name": "TypeScript",
					"size": 22982
				},
				"stargazerCount": 3,
				"url": "https://github.com/Shivam010/Shivam010"
			}
			// ... other repos based on combined metrics of last contribution made and stars on repo
		]
	},
	"statusCode": 200
}
```
