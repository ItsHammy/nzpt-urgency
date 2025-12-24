<?php

// Load data from urgency.sqlite3
$db = new SQLite3('../urgency.sqlite3');

// 54th Parliament Stats
$num_days_sat_54 = $db->querySingle('SELECT COUNT(id) FROM urgency');
$num_days_urgency_54 = $db->querySingle('SELECT COUNT(id) FROM urgency WHERE in_urgency = 1');
$percent_urgency_54 = $num_days_sat_54 > 0 ? round(($num_days_urgency_54 / $num_days_sat_54) * 100, 2) : 0;
$last_updated_54 = file_get_contents('../lastupdate.txt');
$count_bills_affected_54 = $db->querySingle('SELECT COUNT(id) FROM bills');

// 53rd Parliament Stats
$num_days_sat_53 = $db->querySingle('SELECT COUNT(id) FROM legacy WHERE pnum = 53');
$num_days_urgency_53 = $db->querySingle('SELECT COUNT(id) FROM legacy WHERE pnum = 53 AND in_urgency = 1');
$percent_urgency_53 = $num_days_sat_53 > 0 ? round(($num_days_urgency_53 / $num_days_sat_53) * 100, 2) : 0;
$count_bills_affected_53 = $db->querySingle('SELECT COUNT(id) FROM lbills WHERE pnum = 53');
$last_scraped_53 = 'December 24th 2025';


// 52nd Parliament Stats
$num_days_sat_52 = $db->querySingle('SELECT COUNT(id) FROM legacy WHERE pnum = 52');
$num_days_urgency_52 = $db->querySingle('SELECT COUNT(id) FROM legacy WHERE pnum = 52 AND in_urgency = 1');
$percent_urgency_52 = $num_days_sat_52 > 0 ? round(($num_days_urgency_52 / $num_days_sat_52) * 100, 2) : 0;
$count_bills_affected_52 = $db->querySingle('SELECT COUNT(id) FROM lbills WHERE pnum = 52');
$last_scraped_52 = 'December 24th 2025';


// STATIC
$PAGE_UPDATED = "December 24th 2025";
?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Past Parliament Stats - NZPT</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/modern-normalize/1.0.0/modern-normalize.min.css">
    <link rel="stylesheet" href="../assets/style.css">
    <link rel="icon" href="../assets/favicon.ico" type="image/x-icon">
    <script src="assets/script.js"></script>
    <!-- META TAGS -->
    <meta name="description" content="The 54th Parliament of New Zealand has passed <?php echo $count_bills_affected_54; ?> bills under urgency. How does this compare?">
    <meta name="author" content="CJ Sandall">
    <!-- TWITTER CARD META -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:creator" content="@ohitshammy">
    <meta name="twitter:title" content="New Zealand Politics Tracker">
    <meta name="twitter:description" content="The NZ Govt has passed <?php echo $count_bills_affected_54; ?> bills under urgency! How does this compare?">
    <meta name="twitter:image" content="https://nzpt.cjs.nz/assets/nzpt-bannertype.png">
    <!-- OPEN GRAPH META -->
    <meta property="og:title" content="Historical Data">
    <meta property="og:site_name" content="New Zealand Politics Tracker">
    <meta property="og:url" content="https://nzpt.cjs.nz/urgency">
    <meta property="og:description" content="The NZ Govt has passed <?php echo $count_bills_affected_54; ?> bills under urgency! How does this compare?">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://nzpt.cjs.nz/assets/nzpt-bannertype.png">
    <!-- Privacy Analytics -->
     <script defer src="https://cloud.umami.is/script.js" data-website-id="1492dd3b-f626-44b3-a8d5-b074177af097"></script>
</head>
<body>
    <header>
        <h1>NZPT | Urgency Tracker</h1>
        <h5>Compare the previous governments.</h5>
        <nav>
            <a href="../">Urgency Tracker</a>
            <a href="../bills">Bills Viewer</a>
            <a href="../historical" class="active">Historical Data</a>
            <a href="https://cjs.nz/socials" target="_blank">Contact</a>
        </nav>
    </header>
    <main class="historical-stats">
    <h2>A historical lens.</h2>
    <p>
        This page allows you to see the Urgency data from previous New Zealand Parliaments and compare it with the current government. Currently there is data from the 52nd, 53rd and 54th Parliaments, as data preceeding this is less readily available. <b>I am still working on finding older data, and the data provided here may well be inaccurate as it is not currently verified.</b> As always, please raise issues to me via <a href="https://github.com/itshammy/nzpt-urgency/issues" target="_blank">GitHub</a>.
    </p>
    <p class="historical-stats__note"><small>The information on this page is not automatically updated. Last updated <?php echo $PAGE_UPDATED; ?></small></p>

    <div class="stats-overview">
        <article class="stats-card">
            <h3 class="stats-card__title">54th Parliament of New Zealand (2023 - Present)</h3>
            <em>(Last Updated: <?php echo $last_updated_54; ?>)</em>
            <ul>
                <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_54; ?></li>
                <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_54; ?></li>
                <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_54; ?>%</li>
                <li><strong>Total Bills Affected:</strong> <?php echo $count_bills_affected_54; ?></li>
            </ul>
        </article>
        
        <article class="stats-card">
            <h3 class="stats-card__title">53rd Parliament of New Zealand (2020 - 2023)</h3>
            <em>(Last Updated: <?php echo $last_scraped_53; ?>)</em>
            <ul>
                <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_53; ?></li>
                <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_53; ?></li>
            <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_53; ?>%</li>
            <li><strong>Total Bills Affected:</strong> <?php echo $count_bills_affected_53; ?></li>
        </ul>
        </article>
        <article class="stats-card">
            <h3 class="stats-card__title">52nd Parliament of New Zealand (2017 - 2020)</h3>
            <em>(Last Updated: <?php echo $last_scraped_52; ?>)</em>
        <ul>
            <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_52; ?></li>
            <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_52; ?></li>
            <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_52; ?>%</li>
            <li><strong>Total Bills Affected:</strong> <?php echo $count_bills_affected_52; ?></li>
        </ul>
        </article>
</div>
    </main>
    <footer>
        <p>Data is sourced from the <a href="https://www.parliament.nz/en" target="_blank">New Zealand Parliament website</a>. | View the Source Code on <a href="https://github.com/itshammy/nzpt-urgency">GitHub</a>.</p>
        <p>Created by <a href="https://cjs.nz">CJ</a>. Support the project on <a href="https://buymeacoffee.com/hammy">Buy Me a Coffee</a>.</p>
    </footer>
</body>
<script data-name="BMC-Widget" data-cfasync="false" src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="hammy" data-description="Support me on Buy me a coffee!" data-message="This tool was made by a (very) broke student. Consider buying me a coffee if you find this useful!" data-color="#F471FF" data-position="Right" data-x_margin="18" data-y_margin="18"></script>
</html>