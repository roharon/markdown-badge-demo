import azure.functions as func
import logging
import requests

app = func.FunctionApp()


@app.route(route="users/{username}", methods=["GET"], auth_level="anonymous")
def get_contents(req: func.HttpRequest) -> func.HttpResponse:
    try:
        username = req.route_params.get("username")
        languages = fetch_top_3_language(username)
        svg_data = get_template(languages)

        return func.HttpResponse(mimetype="image/svg+xml", body=svg_data)

    except Exception as e:
        logging.error(e)
        return func.HttpResponse(
            mimetype="image/svg+xml",
            body=error_data(),
            status_code=200,
        )


# get github user's top 3 language on github repositories
def fetch_top_3_language(username):
    url = "https://api.github.com/users/{}/repos".format(username)
    response = requests.get(url)
    repos = response.json()

    language_dict = {}
    for repo in repos:
        language = repo["language"]
        if language in language_dict:
            language_dict[language] += 1
        else:
            language_dict[language] = 1

    language_dict.pop(None)
    sorted_language_dict = sorted(
        language_dict.items(), key=lambda x: x[1], reverse=True
    )

    return [item[0] for item in sorted_language_dict[:3]]


def get_template(languages):
    data = []
    rgb_codes = ["#3572A5", "#f1e05a", "#b07219", "#b34c26", "#bfec1a", "#2BA456"]

    for idx, language in enumerate(languages):
        data.append(
            """
            <g xmlns="http://www.w3.org/2000/svg" transform="translate({width}, {height})">
              <g class="stagger" style="animation-delay: 250ms">
                <circle cx="5" cy="6" r="5" fill="{rgb_code}"/>
                <text data-testid="lang-name" x="15" y="10" class="lang-name">{language}</text>
              </g>
            </g>
        """.format(
                language=language,
                rgb_code=rgb_codes[idx % 6],
                width=idx * 120,
                height=0,
            )
        )

    return (
        """\
      <svg xmlns="http://www.w3.org/2000/svg" width="600" height="100" viewBox="0 0 600 100" fill="none" role="img" aria-labelledby="descId">
          <title id="titleId"/>
          <desc id="descId"/>
          <style>
            .header {
              font: 600 22px 'Segoe UI', Ubuntu, Sans-Serif;
              fill: #16537e;
              animation: fadeInAnimation 0.7s ease-in-out forwards;
            }
            @supports(-moz-appearance: auto) {
              /* Selector detects Firefox */
              .header { font-size: 15.5px; }
            }

      @keyframes slideInAnimation {
        from {
          width: 0;
        }
        to {
          width: calc(100%-100px);
        }
      }
      @keyframes growWidthAnimation {
        from {
          width: 0;
        }
        to {
          width: 100%;
        }
      }
      .stat {
        font: 600 14px 'Segoe UI', Ubuntu, "Helvetica Neue", Sans-Serif; fill: #434d58;
      }
      @supports(-moz-appearance: auto) {
        /* Selector detects Firefox */
        .stat { font-size:12px; }
      }
      .bold { font-weight: 700 }
      .lang-name {
        font: 400 14px "Segoe UI", Ubuntu, Sans-Serif;
        fill: #434d58;
      }
      .stagger {
        opacity: 0;
        animation: fadeInAnimation 0.3s ease-in-out forwards;
      }
      #rect-mask rect{
        animation: slideInAnimation 1s ease-in-out forwards;
      }
      .lang-progress{
        animation: growWidthAnimation 0.6s ease-in-out forwards;
      }



        /* Animations */
        @keyframes scaleInAnimation {
          from {
            transform: translate(-5px, 5px) scale(0);
          }
          to {
            transform: translate(-5px, 5px) scale(1);
          }
        }
        @keyframes fadeInAnimation {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
          </style>
          <rect data-testid="card-bg" x="0.5" y="0.5" rx="4.5" height="99%" stroke="#e4e2e2" width="375" fill="#fffefe" stroke-opacity="1"/>
        <g data-testid="card-title" transform="translate(25, 35)">
          <g transform="translate(0, 0)">
            <text x="0" y="0" class="header" data-testid="header">Most Used Languages</text>
          </g>
        </g>


    <g data-testid="main-card-body" transform="translate(0, 65)">
      <svg data-testid="lang-items" x="25">
        <g transform="translate(0, 0)">
          <g transform="translate(0, 0)">
      """
        + "".join(data)
        + """
    </g></g>
      </svg>
          </g>
        </svg>
      """
    )


def error_data():
    return """
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="100" viewBox="0 0 600 100">
    <g transform="translate(0, 50)">
    <text>Can't fetch data</text>
    </g>
    </svg>
    """
