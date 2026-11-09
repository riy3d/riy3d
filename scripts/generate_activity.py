import os
import json
import urllib.request
import datetime
import calendar

USERNAME = "riy3d"
TOKEN = os.environ["GH_TOKEN"]

OUTPUT = "assets/contribution-activity.svg"

today = datetime.datetime.now(datetime.timezone.utc)
start = today - datetime.timedelta(days=365)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = {
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": start.isoformat(),
        "to": today.isoformat()
    }
}

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

if result.get("errors"):
    raise RuntimeError(result["errors"])

user = result["data"]["user"]

if user is None:
    raise RuntimeError("GitHub user not found.")

calendar_data = user["contributionsCollection"]["contributionCalendar"]

days = [
    day
    for week in calendar_data["weeks"]
    for day in week["contributionDays"]
]

total = calendar_data["totalContributions"]

active_days = sum(
    1 for day in days if day["contributionCount"] > 0
)

best_day = max(
    days,
    key=lambda day: day["contributionCount"]
)

average = total / max(len(days), 1)

weekly = [
    sum(
        day["contributionCount"]
        for day in week["contributionDays"]
    )
    for week in calendar_data["weeks"]
]

monthly = {}

for day in days:
    month = day["date"][:7]
    monthly[month] = monthly.get(month, 0) + day["contributionCount"]

months = list(monthly.items())[-6:]

W, H = 1100, 850

svg = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{W}" height="{H}"
     viewBox="0 0 {W} {H}">

<defs>

  <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#080D1B"/>
    <stop offset="100%" stop-color="#15132D"/>
  </linearGradient>

  <linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#38BDF8"/>
    <stop offset="50%" stop-color="#6366F1"/>
    <stop offset="100%" stop-color="#C084FC"/>
  </linearGradient>

  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#6366F1" stop-opacity=".45"/>
    <stop offset="100%" stop-color="#6366F1" stop-opacity="0"/>
  </linearGradient>

  <filter id="glow">
    <feGaussianBlur stdDeviation="7"/>
  </filter>

</defs>

<rect width="100%" height="100%" rx="26" fill="url(#background)"/>

<rect x="2" y="2" width="1096" height="846"
      rx="24" fill="none"
      stroke="#34436B" stroke-opacity=".8"/>

<!-- HEADER -->

<text x="55" y="55"
      fill="#58A6FF"
      font-size="15"
      font-family="Arial"
      font-weight="bold"
      letter-spacing="5">
  RIYAD • GITHUB ANALYTICS
</text>

<text x="55" y="105"
      fill="#FFFFFF"
      font-size="37"
      font-family="Arial"
      font-weight="bold">
  Contribution Dashboard
</text>

<text x="55" y="137"
      fill="#94A3B8"
      font-size="15"
      font-family="Arial">
  BUILDING • LEARNING • ENGINEERING • GROWING
</text>

<circle cx="1020" cy="85" r="8" fill="#22D3EE"/>
<circle cx="1020" cy="85" r="15"
        fill="#22D3EE" opacity=".15"/>

<!-- STAT CARDS -->
"""

cards = [
    ("TOTAL CONTRIBUTIONS", f"{total:,}", "#58A6FF"),
    ("ACTIVE DAYS", f"{active_days:,}", "#A78BFA"),
    ("BEST DAY", f"{best_day['contributionCount']:,}", "#22D3EE"),
    ("DAILY AVERAGE", f"{average:.1f}", "#C084FC")
]

for i, (title, value, color) in enumerate(cards):
    x = 55 + i * 255

    svg += f"""
    <rect x="{x}" y="170" width="230" height="105"
          rx="15" fill="#151E38"
          stroke="#33446B"/>

    <text x="{x+18}" y="204"
          fill="#94A3B8"
          font-size="12"
          font-family="Arial">
      {title}
    </text>

    <text x="{x+18}" y="247"
          fill="{color}"
          font-size="32"
          font-weight="bold"
          font-family="Arial">
      {value}
    </text>
    """

# ACTIVITY GRAPH

left, right = 65, 1035
top, bottom = 350, 475

max_value = max(weekly, default=1) or 1

points = []

for i, value in enumerate(weekly):
    x = left + i * (right-left) / max(len(weekly)-1, 1)
    y = bottom - (value/max_value) * (bottom-top)
    points.append((x, y))

line = " ".join(
    f"{x:.1f},{y:.1f}" for x, y in points
)

area = f"{left},{bottom} {line} {right},{bottom}"

svg += """
<text x="55" y="325"
      fill="#FFFFFF"
      font-size="19"
      font-family="Arial"
      font-weight="bold">
  📈 Contribution Trends
</text>
"""

for i in range(4):
    y = top + i * (bottom-top)/3

    svg += f"""
    <line x1="{left}" y1="{y:.1f}"
          x2="{right}" y2="{y:.1f}"
          stroke="#334155"
          stroke-dasharray="5 8"
          opacity=".6"/>
    """

svg += f"""
<polygon points="{area}" fill="url(#area)"/>

<polyline points="{line}"
          fill="none"
          stroke="url(#neon)"
          stroke-width="12"
          opacity=".3"
          filter="url(#glow)"/>

<polyline points="{line}"
          fill="none"
          stroke="url(#neon)"
          stroke-width="4"
          stroke-linecap="round"
          stroke-linejoin="round"/>
"""

for x, y in points:
    svg += f"""
    <circle cx="{x:.1f}" cy="{y:.1f}"
            r="5" fill="#FFFFFF"
            opacity=".2"/>

    <circle cx="{x:.1f}" cy="{y:.1f}"
            r="2.5" fill="#FFFFFF"/>
    """

# CONTRIBUTION HEATMAP

svg += """
<text x="55" y="535"
      fill="#FFFFFF"
      font-size="19"
      font-family="Arial"
      font-weight="bold">
  Contribution Activity Map
</text>

<text x="55" y="565"
      fill="#94A3B8"
      font-size="12"
      font-family="Arial">
  YOUR DAILY CODING ACTIVITY
</text>
"""

cell = 12
gap = 5
map_x = 85
map_y = 595

levels = [
    "#17213A",
    "#123B66",
    "#155E91",
    "#2563EB",
    "#8B5CF6"
]

for index, day in enumerate(days):

    date = datetime.date.fromisoformat(day["date"])

    week = index // 7
    weekday = date.weekday()

    count = day["contributionCount"]

    if count == 0:
        level = 0
    elif count <= 2:
        level = 1
    elif count <= 5:
        level = 2
    elif count <= 9:
        level = 3
    else:
        level = 4

    x = map_x + week * (cell + gap)
    y = map_y + weekday * (cell + gap)

    svg += f"""
    <rect x="{x}" y="{y}"
          width="{cell}" height="{cell}"
          rx="3"
          fill="{levels[level]}"/>
    """

# MONTHLY ACTIVITY

svg += """
<text x="55" y="735"
      fill="#FFFFFF"
      font-size="18"
      font-family="Arial"
      font-weight="bold">
  Monthly Activity
</text>
"""

for i, (month, value) in enumerate(months):

    x = 55 + i * 170

    label = datetime.datetime.strptime(
        month, "%Y-%m"
    ).strftime("%b %Y")

    bar_width = min(value * 2, 105)

    svg += f"""
    <text x="{x}" y="770"
          fill="#94A3B8"
          font-size="12"
          font-family="Arial">
      {label}
    </text>

    <rect x="{x}" y="783"
          width="105" height="9"
          rx="5" fill="#202D4A"/>

    <rect x="{x}" y="783"
          width="{bar_width}" height="9"
          rx="5" fill="url(#neon)"/>

    <text x="{x}" y="818"
          fill="#FFFFFF"
          font-size="13"
          font-family="Arial">
      {value:,} contributions
    </text>
    """

svg += """
<text x="55" y="835"
      fill="#64748B"
      font-size="12"
      font-family="Arial">
  EVERY CONTRIBUTION IS A STEP FORWARD.
</text>

<text x="1040" y="835"
      fill="#64748B"
      font-size="12"
      text-anchor="end"
      font-family="Arial">
  @riy3d
</text>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as file:
    file.write(svg)

print("Premium Dashboard generated successfully!")
print("Total Contributions:", total)
print("Active Days:", active_days)
print("Best Day:", best_day["date"])
