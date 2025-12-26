<?php header("X-Clacks-Overhead: GNU Terry Pratchett"); ?>
<?php

// Load data from urgency.sqlite3
$db = new SQLite3('urgency.sqlite3');
// Days Sat Info
$num_days_sat = $db->querySingle('SELECT COUNT(id) FROM urgency');
$num_days_urgency = $db->querySingle('SELECT COUNT(id) FROM urgency WHERE in_urgency = 1');
$percent_urgency = $num_days_sat > 0 ? round(($num_days_urgency / $num_days_sat) * 100, 2) : 0;
$last_day_urgent = $db->querySingle('SELECT date FROM urgency WHERE in_urgency = 1 ORDER BY date DESC LIMIT 1');
$last_day_urgent_readable = $last_day_urgent ? (new DateTime($last_day_urgent))->format('d M Y') : 'N/A';
$days_since_urgency = $last_day_urgent ? (new DateTime())->diff(new DateTime($last_day_urgent))->days : 'N/A';
// Bills Info
$count_bills_urgent = $db->querySingle('SELECT COUNT(id) FROM bills');
$billcounter = file_get_contents('billcounter.txt');
$count_bills_all = (int)explode(',', $billcounter)[0];
$billcounter_date = explode(',', $billcounter)[1];
$percent_bills_urgent = $count_bills_all > 0 ? round(($count_bills_urgent / $count_bills_all) * 100, 2) : 0;
// Last Updated
$last_updated = file_get_contents('lastupdate.txt');
?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Urgency Statistics - NZPT</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.1/css/all.min.css" integrity="sha512-2SwdPD6INVrV/lHTZbO2nodKhrnDdJK9/kg2XD1r9uGqPo1cUbujc+IYdlYdEErWNu69gVcYgdxlmVmzTWnetw==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/modern-normalize/1.0.0/modern-normalize.min.css">
    <link rel="stylesheet" href="assets/style.css">
    <link rel="icon" href="assets/favicon.ico" type="image/x-icon">
    <script src="assets/script.js"></script>
    <!-- META TAGS -->
    <meta name="description" content="Free Urgency statistics for the 54th Parliament of New Zealand. Sourced from the Parliament website and made easy to reference.">
    <meta name="keywords" content="New Zealand, Government, Parliament, Urgency, Politics, Statistics, CJS, Regulatory Standards Bill, COVID-19, Legislation">
    <meta name="author" content="CJ Sandall">
    <!-- TWITTER CARD META -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:creator" content="@ohitshammy">
    <meta name="twitter:title" content="Urgency Tracker - New Zealand Politics Tracker">
    <meta name="twitter:description" content="The NZ Govt has passed <?php echo $count_bills_affected; ?> bills under urgency!">
    <meta name="twitter:image" content="https://nzpt.cjs.nz/assets/nzpt-bannertype.png">
    <!-- OPEN GRAPH META -->
    <meta property="og:title" content="The New Zealand Politics Tracker by CJS">
    <meta property="og:site_name" content="Urgency Tracker - NZPT">
    <meta property="og:url" content="https://nzpt.cjs.nz/urgency">
    <meta property="og:description" content="The NZ Govt has passed <?php echo $count_bills_affected; ?> bills under urgency! See all the stats for free!">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://nzpt.cjs.nz/assets/nzpt-bannertype.png">
    <!-- Privacy Analytics -->
     <script defer src="https://cloud.umami.is/script.js" data-website-id="1492dd3b-f626-44b3-a8d5-b074177af097"></script>
</head>
<body>
    <header>
        <h1>NZPT | Urgency Tracker</h1>
        <h5>A free tool by CJ Sandall.</h5>
        <nav>
            <a href="#" class="active">Urgency Tracker</a>
            <a href="bills/">Bills Viewer</a>
            <a href="historical/">Historical Data</a>
            <a href="https://cjs.nz/socials" target="_blank">Contact</a>
        </nav>
    </header>
    <main class="stats-overview">
        <div id="at-a-glance">
        <h2>54th Parliament Statistics:</h2>
            <div class="stats-card-grid">
                <div class="stats-card" id="day-sat">
                    <h2><span id="num-days-sat"><?php echo $num_days_sat; ?></span></h2>
                    <p title="Sitting days can span multiple calendar days. Sitting days are counted as the number of days the Parliament was in session, which may include partial days.">Sitting Days. <small><i class="fa-solid fa-circle-info"></i></small></p>
                </div>
                <div class="stats-card" id="day-urgency">
                    <h2 class="stats-card__title"><span id="num-days-urgency"><?php echo $num_days_urgency; ?></span></h2>
                    <p>Days in Urgency.</p>
                    <small>Share This: <a target="_blank" href="https://twitter.com/intent/tweet?text=Did you know this parliament has spent <?php echo $num_days_urgency; ?> days under urgency? via nzpt.cjs.nz %23nzpol"><i class="fa-brands fa-twitter"></i> Twitter</a> | <a target="_blank"href="https://bsky.app/intent/compose?text=Did you know this parliament has spent <?php echo $num_days_urgency; ?> days under urgency? via nzpt.cjs.nz %23nzpol"><i class="fa-brands fa-bluesky"></i> Bluesky</a></small>
                </div>
                <div class="stats-card" id="p-urgency">
                    <h2 class="stats-card__title"><span id="num-percent-urgency"><?php echo $percent_urgency; ?></span>%</h2>
                    <p>Percentage of days in Urgency.</p>
                    <small>Share This: <a target="_blank" href="https://twitter.com/intent/tweet?text=Did you know the current Parliament has spent <?php echo $percent_urgency; ?>%25 of their days in urgency?! Source: nzpt.cjs.nz %23nzpol"><i class="fa-brands fa-twitter"></i> Twitter</a> | <a target="_blank"href="https://bsky.app/intent/compose?text=Did you know the current Parliament has spent <?php echo $percent_urgency; ?>% of their days in urgency?! Source: nzpt.cjs.nz %23nzpol"><i class="fa-brands fa-bluesky"></i> Bluesky</a></small>
                </div>
                <div class="stats-card" id="total-bills">
                    <h2 class="stats-card__title"><span id="num-percent-urgency"><?php echo $count_bills_all; ?></span></h2>
                    <p>Bills considered by this Parliament.</p>
                    <small title="The official bill count is not published until after a Parliament term has concluded. The number displayed on NZPT is calculated daily by scraping the Parliament website. This number includes Government Bills, Local Bills, and Member Bills.">Estimate as of <?php echo $billcounter_date; ?> <i class="fa-solid fa-circle-info"></i></small>
                </div>
                <div class="stats-card" id="bills-under-urgency">
                    <h2 class="stats-card__title"><span id="num-percent-urgency"><?php echo $count_bills_urgent; ?></span></h2>
                    <p title="This does not mean all parts of the bill were under urgency, but just one or more parts were.">Bills under Urgency. <small><i class="fa-solid fa-circle-info"></i></small></p>
                    <small>Share This: <a target="_blank" href="https://twitter.com/intent/tweet?text=Did you know that this Parliament has considered <?php echo $count_bills_urgent; ?> bills under urgency? Source nzpt.cjs.nz %23nzpol"><i class="fa-brands fa-twitter"></i> Twitter</a> | <a target="_blank"href="https://bsky.app/intent/compose?text=Did you know that this Parliament has considered <?php echo $count_bills_urgent; ?> bills under urgency? Source nzpt.cjs.nz %23nzpol"><i class="fa-brands fa-bluesky"></i> Bluesky</a></small>
                </div>
                <div class="stats-card" id="percentage-bills-urgency">
                    <h2 class="stats-card__title"><span id="num-percent-urgency"><?php echo $percent_bills_urgent; ?></span>%</h2>
                    <p title="This does not mean all parts of the bill were under urgency, but just one or more parts were.">Bills under Urgency.</p>
                    <small>Share This: <a target="_blank" href="https://twitter.com/intent/tweet?text=Did you know that <?php echo $percent_bills_urgent; ?>%25 of bills considered by this Parliament were under urgency? Source nzpt.cjs.nz %23nzpol"><i class="fa-brands fa-twitter"></i> Twitter</a> | <a target="_blank"href="https://bsky.app/intent/compose?text=Did you know that <?php echo $percent_bills_urgent; ?>%25 of bills considered by this Parliament were under urgency? Source nzpt.cjs.nz %23nzpol"><i class="fa-brands fa-bluesky"></i> Bluesky</a></small>
                </div>
                <!-- Temporarily hidden stats, will be re-added once useful
                <div class="stats-card" id="most-recent-urgency">
                    <h2 class="stats-card__title"><span id="last-day-urgent"><?php echo $last_day_urgent_readable; ?></span></h2>
                    <p>Most recent day in Urgency.</p>
                </div>
                <div class="stats-card" id="days-since-urgency">
                    <h2 class="stats-card__title"><span id="days-since-urgency"><?php echo $days_since_urgency; ?></span></h2>
                    <p>Days since last Urgency Motion.</p>
                </div>
                -->
            </div>
        <a href="historical/" class="button">How does this stack against previous parliaments?</a>
        <p><strong>Last Updated:</strong> <span id="last-updated"><?php echo $last_updated; ?></span></p>
        </div>
        <hr>
        <div id="explainer-content">
            <h2>Who are you, why do you care?</h2>
            <p>
            When the New Zealand Parliament goes into urgency, it allows the typical process of lawmaking to be expedited. This means that steps such as public consultation (when the public can give feedback on proposed laws) and select committee review (where a smaller group of MPs scrutinise a bill in detail) can be skipped or shortened.
            </p>

            <p>
            Urgency is designed to allow the government to pass legislation quickly in response to unexpected or genuinely urgent situations. Recent events that warranted urgency include the COVID-19 pandemic and the 2019 terror attacks in Ōtautahi Christchurch.
            </p>

            <p>
            In recent months, however, urgency has been increasingly used by the 54th Parliament to bypass public consultation and select committee hearings in order to rush the coalition government’s legislative agenda through Parliament.
            </p>

            <p>
            I care about this issue, as do many New Zealanders, because the urgency process removes the public's ability to have their say and makes it harder for opposition parties to scrutinise legislation before it becomes law. While many laws have been passed under urgency, not all of them appear to be genuinely urgent.
            </p>

            <p>
            I am not an expert coder; however, I could not find an existing tool like this online, so I built one myself to track urgency statistics in the 54th Parliament. I plan to make more NZPOL tools in the future, and would appreciate any support, either on <a href="https://cjs.nz/socials" target="_blank">my social media</a> or by <a href="https://buymeacoffee.com/hammy" target="_blank">buying me a coffee</a>!
            </p>
            <hr>
            <h2>The Statistics</h2>
            <?php echo "<p>The 54th Parliament has officially sat for $num_days_sat days since it was formed on 3rd December 2023. In that time, the coalition government which consists of the National Party, The ACT Party, and New Zealand First, has put the parliament into Urgency on $num_days_urgency occasions to pass $count_bills_affected bills without the normal amount of consultation and scrutiny. This makes up $percent_urgency% of all sitting days, with the most recent urgency session being $days_since_urgency days ago on $last_day_urgent_readable. These statistics are scraped from the New Zealand Parliament website, and is updated daily by the NZPT urgency tracker. The urgency tracker system can be seen on Github for those more technically minded. The tracker is a passion project by CJ and will eventually have information about bills affected. The tracker was last updated on $last_updated and last manually checked on December 23rd 2025.</p>";?>
        </div>
    </main>
    <footer>
        <p>Data is sourced from the <a href="https://www.parliament.nz/en" target="_blank">New Zealand Parliament website</a>. | View the Source Code on <a href="https://github.com/itshammy/nzpt-urgency" target="_blank">GitHub</a>.</p>
        <p>Created by <a href="https://cjs.nz">CJ</a>.<br><a href="https://www.buymeacoffee.com/hammy"><img width="10%" src="https://img.buymeacoffee.com/button-api/?text=Buy me a Latte&emoji=☕&slug=hammy&button_colour=BD5FFF&font_colour=ffffff&font_family=Poppins&outline_colour=000000&coffee_colour=FFDD00" /></a></p>
    </footer>
</body>
<script data-name="BMC-Widget" data-cfasync="false" src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="hammy" data-description="Support me on Buy me a coffee!" data-message="This tool was made by a (very) broke student. Consider buying me a coffee if you find this useful!" data-color="#F471FF" data-position="Right" data-x_margin="18" data-y_margin="18"></script>
</html>