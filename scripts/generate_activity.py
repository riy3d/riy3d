import os
import json
import urllib.request
import datetime
import html

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

calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]

days = [
    day
    for week in calendar["weeks"]
    for day in week["contributionDays"]
]

total = calendar["totalContributions"]
active = sum(1 for day in days if day["contributionCount"] > 0)
best = max((day["contributionCount"] for day in days), default=0)

weekly = [
    sum(day["contributionCount"] for day in week["contributionDays"])
    for week in calendar["weeks"]
]

W, H = 1100, 600
left, right = 75, 1050
top, bottom = 245, 445

max_value = max(weekly, default=1) or 1

points = []

for i, value in enumerate(weekly):
    x = left + i * (right - left) / max(len(weekly) - 1, 1)
    y = bottom - (value / max_value) * (bottom - top)
    points.append((x, y))

line = " ".join(
    f"{x:.1f},{y:.1f}" for x, y in points
)

area = (
    f"{left},{bottom} "
    + line
    + f" {right},{bottom}"
)

svg = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{W}" height="{H}"
     viewBox="0 0 {W} {H}">

<defs>

  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#080D1B"/>
    <stop offset="100%" stop-color="#11152D"/>
  </linearGradient>

  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#38BDF8"/>
    <stop offset="50%" stop-color="#6366F1"/>
    <stop offset="100%" stop-color="#C084FC"/>
  </linearGradient>

  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#6366F1" stop-opacity=".45"/>
    <stop offset="100%" stop-color="#6366F1" stop-opacity="0"/>
  </linearGradient>

  <filter id="glow">
    <feGaussianBlur stdDeviation="5"/>
  </filter>

</defs>

<rect width="100%" height="100%" rx="24" fill="url(#bg)"/>

<rect x="2" y="2" width="1096" height="596"
      rx="22" fill="none"
      stroke="#27365B" stroke-opacity=".8"/>

<text x="55" y="65" fill="#58A6FF"
      font-size="17" font-family="Arial"
      font-weight="bold" letter-spacing="4">
  GITHUB ANALYTICS
</text>

<text x="55" y="115" fill="#FFFFFF"
      font-size="36" font-family="Arial"
      font-weight="bold">
  Contribution Activity
</text>

<text x="55" y="150" fill="#94A3B8"
      font-size="16" font-family="Arial">
  RIYAD • DREAM • CODE • INNOVATE
</text>

<g font-family="Arial">

  <rect x="55" y="175" width="230" height="95"
        rx="14" fill="#151E38" stroke="#263B66"/>

  <text x="75" y="207" fill="#94A3B8" font-size="13">
    TOTAL CONTRIBUTIONS
  </text>

  <text x="75" y="248" fill="#58A6FF"
        font-size="31" font-weight="bold">
    {total:,}
  </text>

  <rect x="310" y="175" width="230" height="95"
        rx="14" fill="#151E38" stroke="#263B66"/>

  <text x="330" y="207" fill="#94A3B8" font-size="13">
    ACTIVE DAYS
  </text>

  <text x="330" y="248" fill="#A78BFA"
        font-size="31" font-weight="bold">
    {active:,}
  </text>

  <rect x="565" y="175" width="230" height="95"
        rx="14" fill="#151E38" stroke="#263B66"/>

  <text x="585" y="207" fill="#94A3B8" font-size="13">
    BEST DAY
  </text>

  <text x="585" y="248" fill="#22D3EE"
        font-size="31" font-weight="bold">
    {best:,}
  </text>

  <rect x="820" y="175" width="225" height="95"
        rx="14" fill="#151E38" stroke="#263B66"/>

  <text x="840" y="207" fill="#94A3B8" font-size="13">
    DAILY AVERAGE
  </text>

  <text x="840" y="248" fill="#FFFFFF"
        font-size="31" font-weight="bold">
    {total / max(len(days), 1):.1f}
  </text>

</g>

"""

for i in range(5):
    y = top + i * (bottom - top) / 4
    svg += f"""
    <line x1="{left}" y1="{y:.1f}"
          x2="{right}" y2="{y:.1f}"
          stroke="#293653" stroke-opacity=".65"
          stroke-dasharray="5 8"/>
    """

svg += f"""
<polygon points="{area}" fill="url(#area)"/>

<polyline points="{line}"
          fill="none"
          stroke="url(#line)"
          stroke-width="9"
          opacity=".25"
          filter="url(#glow)"/>

<polyline points="{line}"
          fill="none"
          stroke="url(#line)"
          stroke-width="4"
          stroke-linecap="round"
          stroke-linejoin="round"/>
"""

for x, y in points:
    svg += f"""
    <circle cx="{x:.1f}" cy="{y:.1f}" r="5"
            fill="#FFFFFF" opacity=".15"/>
    <circle cx="{x:.1f}" cy="{y:.1f}" r="2.8"
            fill="#FFFFFF"/>
    """

svg += """
<text x="55" y="490" fill="#58A6FF"
      font-size="15" font-family="Arial"
      font-weight="bold">
  CONSISTENCY • GROWTH • ENGINEERING
</text>

<text x="55" y="545" fill="#64748B"
      font-size="14" font-family="Arial">
  EVERY CONTRIBUTION IS A STEP FORWARD.
</text>

<text x="1045" y="545" text-anchor="end"
      fill="#64748B" font-size="13"
      font-family="Arial">
  @riy3d
</text>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as file:
    file.write(svg)

print("Contribution Dashboard generated successfully!")
print(f"Total Contributions: {total}")
