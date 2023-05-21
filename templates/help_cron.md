:information_source: Command `cron`

Syntax to use: `cron <cron>, <reminder>`

Examples:
`cron 0 8 * * 1, wake up` sends `wake up` every Monday at 8
`cron 0 16 1 * *, run backups` sends `run backups` every 1st day of the month at 16
`cron 30 11 */5 */2 *, look out` sends `look out` every 5/10/15/20/25th on even months (February, April, June...) at 11:30

For more information on cron syntax, read this: https://en.wikipedia.org/wiki/Cron