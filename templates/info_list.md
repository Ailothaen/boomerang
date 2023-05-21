:information_source: Here are your current and upcoming reminders:

{% if reminders|length > 0 %}
{% for reminder in reminders %}
`{{ reminder["id"] }}` – "{{ reminder["text"]}}" – Next occurrence: <t:{{ reminder["date_next"] }}> {% if reminder["recurrence"] %}(repeated every {{ reminder["recurrence"] }}){% endif %}

{% endfor %}
{% else %}
*No reminders*
{% endif %}

To remove a reminder, use the `remove` command, followed by the number of the reminder.