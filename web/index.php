<?php

// Load data from urgency.sqlite3
$db = new SQLite3('urgency.sqlite3');
$num_days_sat = $db->querySingle('SELECT COUNT(id) FROM urgency');
$num_days_urgency = $db->querySingle('SELECT COUNT(id) FROM urgency WHERE in_urgency = 1');
$percent_urgency = $num_days_sat > 0 ? round(($num_days_urgency / $num_days_sat) * 100, 2) : 0;
$last_day_urgent = $db->querySingle('SELECT date FROM urgency WHERE in_urgency = 1 ORDER BY date DESC LIMIT 1');
$last_day_urgent_readable = $last_day_urgent ? (new DateTime($last_day_urgent))->format('d M Y') : 'N/A';
$days_since_urgency = $last_day_urgent ? (new DateTime())->diff(new DateTime($last_day_urgent))->days : 'N/A';
$last_updated = file_get_contents('lastupdate.txt');
$count_bills_affected = $db->querySingle('SELECT COUNT(id) FROM bills');

?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Urgency Statistics - NZPT</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
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
    <meta property="og:title" content="How long has the New Zealand Government spend in Urgency?">
    <meta property="og:site_name" content="Urgency Tracker - NZPT">
    <meta property="og:url" content="https://nzpt.cjs.nz/urgency">
    <meta property="og:description" content="The NZ Govt has passed <?php echo $count_bills_affected; ?> bills under urgency! See all the stats for free!">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://nzpt.cjs.nz/assets/nzpt-bannertype.png">
</head>
<body>
    <header>
        <h1>NZPT | Urgency Tracker</h1>
        <h5>A free tool by CJ Sandall.</h5>
        <nav>
            <a href="#" class="active">Urgency Tracker</a>
            <a href="bills/">Bills Viewer</a>
            <a href="https://cjs.nz/socials" target="_blank">Contact</a>
        </nav>
    </header>
    <h2>54th Parliament Statistics:</h2>
    <div class="statistics">
        <div class="statistics-box" id="day-sat">
            <h3><span id="num-days-sat"><?php echo $num_days_sat; ?></span></h3>
            <p>Days sat by the 54th Parliament.</p>
        </div>
        <div class="statistics-box" id="day-urgency">
            <h3><span id="num-days-urgency"><?php echo $num_days_urgency; ?></span></h3>
            <p>Days in Urgency.</p>
            <small><a target="_blank" href="https://twitter.com/intent/tweet?text=There%20has%20been%20<?php echo $num_days_urgency; ?>%20days%20that%20the%2054th%20(coalition-led)%20New%20Zealand%20Parliament%20have%20passed%20bills%20under%20urgency%2C%20avoiding%20public%20scrutiny.%20%23NZPOL%20Source%3A&url=https%3A%2F%2Fnzpt.cjs.nz%2F">Tweet this.</a></small>
        </div>
        <div class="statistics-box" id="percent-urgency">
            <h3><span id="num-percent-urgency"><?php echo $percent_urgency; ?></span>%</h3>
            <p>Percentage of days in Urgency.</p>
            <small><a target="_blank" href="https://twitter.com/intent/tweet?text=Did%20you%20know%20that%20<?php echo $percent_urgency; ?>%25%20of%20the%2054th%20New%20Zealand%20Parliament%20sitting%20days%20has%20been%20in%20urgency%3F&url=https%3A%2F%2Fnzpt.cjs.nz%2F">Tweet this.</a></small>
        </div>
        <div class="statistics-box" id="percent-urgency">
            <h3><span id="num-percent-urgency"><?php echo $count_bills_affected; ?></span></h3>
            <p title="This does not mean all parts of the bill were under urgency, but just one or more parts were.">Bills under Urgency.</p>
            <small><a target="_blank" href="https://twitter.com/intent/tweet?text=Under%20this%20government%2C%20the%20New%20Zealand%20Parliament%20has%20passed%20<?php echo $count_bills_affected; ?>%20bills%20under%20urgency!%20%23nzpol%20Source%3A&url=https%3A%2F%2Fnzpt.cjs.nz%2F">Tweet this.</a></small>
        </div>
        <div class="statistics-box" id="percent-urgency">
            <h3><span id="last-day-urgent"><?php echo $last_day_urgent_readable; ?></span></h3>
            <p>Most recent day in Urgency.</p>
        </div>
        <div class="statistics-box" id="percent-urgency">
            <h3><span id="days-since-urgency"><?php echo $days_since_urgency; ?></span></h3>
            <p>Days since last Urgency.</p>
            <small><a target="_blank" href="https://twitter.com/intent/tweet?text=There%20has%20been%20<?php echo $days_since_urgency; ?>%20days%20since%20the%20NZ%20Government%20has%20been%20in%20Urgency!%20Check%20the%20stats%20here%3A&url=https%3A%2F%2Fnzpt.cjs.nz%2F">Tweet this.</a></small>
        </div>
    </div>
    <p><strong>Last Updated:</strong> <span id="last-updated"><?php echo $last_updated; ?></span></p>
    <hr>
    <main id="explainer-content">
        <h1>Who are you, why do you care?</h1>
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
        <?php echo "<p>The 54th Parliament has officially sat for $num_days_sat days since it was formed on 3rd December 2023. In that time, the coalition government conisiting of the National Party, The ACT Party, and New Zealand First, has put the parliament into Urgency on $num_days_urgency occasions to pass $count_bills_affected bills without the normal amount of consultation and scrutiny. This makes up $percent_urgency% of all sitting days, with the most recent urgency session being $days_since_urgency days ago on $last_day_urgent_readable. These statistics are scraped from the New Zealand Parliament website, and is updated daily by the NZPT urgency tracker. The urgency tracker system can be seen on Github for those more technically minded. The tracker is a passion project by CJ and will eventually have information about bills affected. The tracker was last updated on $last_updated and last manually checked on December 23rd 2025.</p>";?>
    </main>
    <section id="faqs">
        <h2>Frequently Asked Questions (FAQs)</h2>
        <h3>What is Urgency?</h3>
        <p>Urgency is a parliamentary procedure that allows the government to expedite the legislative process for certain bills. When a bill is declared urgent, it can bypass some of the usual stages of scrutiny, allowing it to be debated and passed more quickly than under normal circumstances.</p>
        
        <h3>What are "sitting days"?</h3>
        <p>Sitting Days refer to the days when the New Zealand Parliament is officially in session and conducting its business. These are the days when members of Parliament (should*) meet to debate, discuss, and make decisions on legislative matters. A sitting day can span one or more days if the parliament enters Urgency.</p>
        
        <h3>Where does the data come from?</h3>
        <p>The data is sourced from the official New Zealand Parliament website, ensuring accuracy and reliability. You can check out the code yourself <a href="https://github.com/itshammy/nzpt-urgency" target="_blank">on GitHub</a>.</p>
    </section>
    <footer>
        <p>Data is sourced from the <a href="https://www.parliament.nz/en" target="_blank">New Zealand Parliament website</a>. | View the Source Code on <a href="https://github.com/itshammy/nzpt-urgency">GitHub</a>.</p>
        <p>Created by <a href="https://cjs.nz">CJ</a>. Support the project on <a href="https://buymeacoffee.com/hammy">Buy Me a Coffee</a>.</p>
    </footer>
</body>
<script data-name="BMC-Widget" data-cfasync="false" src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="hammy" data-description="Support me on Buy me a coffee!" data-message="This tool was made by a (very) broke student. Consider buying me a coffee if you find this useful!" data-color="#F471FF" data-position="Right" data-x_margin="18" data-y_margin="18"></script>
</html>