<?php

// Load data from urgency.sqlite3
$db = new SQLite3('../urgency.sqlite3');

// 54th Parliament Stats
$num_days_sat_54 = $db->querySingle('SELECT COUNT(id) FROM urgency');
$num_days_urgency_54 = $db->querySingle('SELECT COUNT(id) FROM urgency WHERE in_urgency = 1');
$percent_urgency_54 = $num_days_sat_54 > 0 ? round(($num_days_urgency_54 / $num_days_sat_54) * 100, 2) : 0;
$last_updated_54 = file_get_contents('../lastupdate.txt');
$count_bills_affected_54 = $db->querySingle('SELECT COUNT(id) FROM bills');
$count_total_bills_54 = (int)explode(',', (file_get_contents('../billcounter.txt')))[0];
$ratio_urgent_54 = $count_total_bills_54 > 0 ? round(($count_bills_affected_54 / $count_total_bills_54) * 100, 2) : 0;

// 53rd Parliament Stats
$num_days_sat_53 = $db->querySingle('SELECT COUNT(id) FROM legacy WHERE pnum = 53');
$num_days_urgency_53 = $db->querySingle('SELECT COUNT(id) FROM legacy WHERE pnum = 53 AND in_urgency = 1');
$percent_urgency_53 = $num_days_sat_53 > 0 ? round(($num_days_urgency_53 / $num_days_sat_53) * 100, 2) : 0;
$count_bills_affected_53 = $db->querySingle('SELECT COUNT(id) FROM lbills WHERE pnum = 53');
$count_total_bills_53 = '275';
$ratio_urgent_53 = $count_total_bills_53 > 0 ? round(($count_bills_affected_53 / $count_total_bills_53) * 100, 2) : 0;
$last_scraped_53 = 'December 24th 2025';


// 52nd Parliament Stats
$num_days_sat_52 = $db->querySingle('SELECT COUNT(id) FROM legacy WHERE pnum = 52');
$num_days_urgency_52 = $db->querySingle('SELECT COUNT(id) FROM legacy WHERE pnum = 52 AND in_urgency = 1');
$percent_urgency_52 = $num_days_sat_52 > 0 ? round(($num_days_urgency_52 / $num_days_sat_52) * 100, 2) : 0;
$count_bills_affected_52 = $db->querySingle('SELECT COUNT(id) FROM lbills WHERE pnum = 52');
$count_total_bills_52 = '283';
$ratio_urgent_52 = $count_total_bills_52 > 0 ? round(($count_bills_affected_52 / $count_total_bills_52) * 100, 2) : 0;
$last_scraped_52 = 'December 24th 2025';

// START pdf-scraped data

// 51st Parliament Stats
$num_days_sat_51 = '251';
$num_days_urgency_51 = '26';
$percent_urgency_51 = $num_days_sat_51 > 0 ? round(($num_days_urgency_51 / $num_days_sat_51) * 100, 2) : 0;
$count_bills_affected_51 = '66';
$count_total_bills_51 = '305';
$ratio_urgent_51 = $count_total_bills_51 > 0 ? round(($count_bills_affected_51 / $count_total_bills_51) * 100, 2) : 0;

// 50th Parliament Stats
$num_days_sat_50 = '227';
$num_days_urgency_50 = '36';
$percent_urgency_50 = $num_days_sat_50 > 0 ? round(($num_days_urgency_50 / $num_days_sat_50) * 100, 2) : 0;
$count_bills_affected_50 = '144';
$count_total_bills_50 = '300';
$ratio_urgent_50 = $count_total_bills_50 > 0 ? round(($count_bills_affected_50 / $count_total_bills_50) * 100, 2) : 0;

// 49th Parliament Stats
$num_days_sat_49 = '230';
$num_days_urgency_49 = '29';
$percent_urgency_49 = $num_days_sat_49 > 0 ? round(($num_days_urgency_49 / $num_days_sat_49) * 100, 2) : 0;
$count_bills_affected_49 = '68';
$count_total_bills_49 = '352';
$ratio_urgent_49 = $count_total_bills_49 > 0 ? round(($count_bills_affected_49 / $count_total_bills_49) * 100, 2) : 0; 

// 48th Parliament Stats
$num_days_sat_48 = '246';
$num_days_urgency_48 = '26';
$percent_urgency_48 = $num_days_sat_48 > 0 ? round(($num_days_urgency_48 / $num_days_sat_48) * 100, 2) : 0;
$count_bills_affected_48 = '66';
$count_total_bills_48 = '294';
$ratio_urgent_48 = $count_total_bills_48 > 0 ? round(($count_bills_affected_48 / $count_total_bills_48) * 100, 2) : 0;  


// STATIC
$PAGE_UPDATED = "December 26th 2025";
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
    <!-- Charts.js -->
     <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
    <main class="stats-overview">
    <h2>A historical lens.</h2>
    <p>
        This page allows you to see the Urgency data from previous New Zealand Parliaments and compare it with the current government. Currently there is data from the 52nd, 53rd and 54th Parliaments, as data preceeding this is less readily available. <b>I am still working on finding older data, and the data provided here may well be inaccurate as it is not currently verified.</b> As always, please raise issues to me via <a href="https://github.com/itshammy/nzpt-urgency/issues" target="_blank">GitHub</a>.
    </p>
    <p class="historical-stats__note"><small>Some of the information on this page is not automatically updated. Last updated <?php echo $PAGE_UPDATED; ?></small></p>

    <div class="stats-card-grid">
        <article class="stats-card">
            <h3 class="stats-card__title">54th Parliament of New Zealand (2023 - Present)</h3>
            <em>(As of <?php echo $last_updated_54; ?>)</em>
            <ul>
                <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_54; ?></li>
                <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_54; ?></li>
                <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_54; ?>%</li>
                <li><strong>Total Bills Urgent:</strong> <?php echo $count_bills_affected_54; ?></li>
                <li><strong>Total Bills:</strong> <?php echo $count_total_bills_54; ?> <span title="The official bill count is not published until after a Parliament term has concluded. The number displayed on NZPT is calculated daily by scraping the Parliament website. This number includes Government Bills, Local Bills, and Member Bills."><i class="fa-solid fa-circle-info"></i></span></small></li>
                <li><strong>Ratio of urgent bills:</strong> <?php echo $ratio_urgent_54; ?>% </li>
            </ul>
        </article>
        
        <article class="stats-card">
            <h3 class="stats-card__title">53rd Parliament of New Zealand (2020 - 2023)</h3>
            <ul>
            <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_53; ?></li>
            <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_53; ?></li>
            <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_53; ?>%</li>
            <li><strong>Total Bills Urgent:</strong> <?php echo $count_bills_affected_53; ?></li>
            <li><strong>Total Bills:</strong> <?php echo $count_total_bills_53; ?></li>
            <li><strong>Ratio of urgent bills:</strong> <?php echo $ratio_urgent_53; ?>%</li>
        </ul>
        </article>
        <article class="stats-card">
            <h3 class="stats-card__title">52nd Parliament of New Zealand (2017 - 2020)</h3>
        <ul>
            <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_52; ?></li>
            <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_52; ?></li>
            <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_52; ?>%</li>
            <li><strong>Total Bills Urgent:</strong> <?php echo $count_bills_affected_52; ?></li>
            <li><strong>Total Bills:</strong> <?php echo $count_total_bills_52; ?></li>
            <li><strong>Ratio of urgent bills:</strong> <?php echo $ratio_urgent_52; ?>%</li>
        </ul>
        </article>
        <article class="stats-card">
            <h3 class="stats-card__title">51st Parliament of New Zealand (2014 - 2017)</h3>
        <ul>
            <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_51; ?></li>
            <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_51; ?></li>
            <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_51; ?>%</li>
            <li><strong>Total Bills Urgent:</strong> <?php echo $count_bills_affected_51; ?></li>
            <li><strong>Total Bills:</strong> <?php echo $count_total_bills_51; ?></li>
            <li><strong>Ratio of urgent bills:</strong> <?php echo $ratio_urgent_51; ?>%</li>
        </ul>
        </article>
        <article class="stats-card">
            <h3 class="stats-card__title">50th Parliament of New Zealand (2011 - 2014)</h3>
        <ul>
            <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_50; ?></li>
            <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_50; ?></li>
            <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_50; ?>%</li>
            <li><strong>Total Bills Urgent:</strong> <?php echo $count_bills_affected_50; ?></li>
            <li><strong>Total Bills:</strong> <?php echo $count_total_bills_50; ?></li>
            <li><strong>Ratio of urgent bills:</strong> <?php echo $ratio_urgent_50; ?>%</li>
        </ul>
        </article>
        <article class="stats-card">
            <h3 class="stats-card__title">49th Parliament of New Zealand (2008 - 2011)</h3>
        <ul>
            <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_49; ?></li>
            <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_49; ?></li>
            <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_49; ?>%</li>
            <li><strong>Total Bills Urgent:</strong> <?php echo $count_bills_affected_49; ?></li>
            <li><strong>Total Bills:</strong> <?php echo $count_total_bills_49; ?></li>
            <li><strong>Ratio of urgent bills:</strong> <?php echo $ratio_urgent_49; ?>%</li>
        </ul>
        </article>
        <article class="stats-card">
            <h3 class="stats-card__title">48th Parliament of New Zealand (2005 - 2008)</h3>
        <ul>
            <li><strong>Total Days Sat:</strong> <?php echo $num_days_sat_48; ?></li>
            <li><strong>Total Days in Urgency:</strong> <?php echo $num_days_urgency_48; ?></li>
            <li><strong>Percentage of Days in Urgency:</strong> <?php echo $percent_urgency_48; ?>%</li>
            <li><strong>Total Bills Urgent:</strong> <?php echo $count_bills_affected_48; ?></li>
            <li><strong>Total Bills:</strong> <?php echo $count_total_bills_48; ?></li>
            <li><strong>Ratio of urgent bills:</strong> <?php echo $ratio_urgent_48; ?>%</li>
        </ul>
        </article>
</div>
<hr>
<div class="graph" id="graph">
    <h2>Urgency over Time</h2>
    <canvas id="urgencyRatio"></canvas>
</div>
<hr>
<aside class="historical-stats__info" id="disclaimer">
    <h4>About this data</h4>
    <p>Historical data is sourced from the Sessional Journals Archive. This includes all data from 48th to 52nd Parliaments. Data from the 53rd Parliament was manually complied from the Sessional Journals. Data on the current (54th) Parliament is sourced using the main <a href="https://nzpt.cjs.nz">NZPT urgency tool.</a></p>
    <p>Total Bill Count and Ratio of Urgent Bills include all bills seen by that parliament, including unsuccessful bills and bills carried over from the preceding parliament.</p>
</aside>
    </main>
    <footer>
        <p>Data is sourced from the <a href="https://www.parliament.nz/en" target="_blank">New Zealand Parliament website</a>. | View the Source Code on <a href="https://github.com/itshammy/nzpt-urgency" target="_blank">GitHub</a>.</p>
        <p>Created by <a href="https://cjs.nz">CJ</a>.<br><a href="https://www.buymeacoffee.com/hammy"><img width="10%" src="https://img.buymeacoffee.com/button-api/?text=Buy me a Latte&emoji=☕&slug=hammy&button_colour=BD5FFF&font_colour=ffffff&font_family=Poppins&outline_colour=000000&coffee_colour=FFDD00" /></a></p>
    </footer>
</body>
</html>
<!-- CHART SCRIPT -->
 <script>
  const ctx = document.getElementById('urgencyRatio');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Parliament 48 (2005-2008)', 'Parliament 49 (2008 - 2011)', 'Parliament 50 (2011 - 2014)', 'Parliament 51 (2014 - 2017)', 'Parliament 52 (2017 - 2020)', 'Parliament 53 (2020 - 2023)', 'Parliament 54 (2023 - Present)'],
      datasets: [{
        label: 'Percentage of Bills Passed Under Urgency',
        data: [<?php echo $ratio_urgent_48; ?>, <?php echo $ratio_urgent_49; ?>, <?php echo $ratio_urgent_50; ?>, <?php echo $ratio_urgent_51; ?>, <?php echo $ratio_urgent_52; ?>, <?php echo $ratio_urgent_53; ?>, <?php echo $ratio_urgent_54; ?>],
        borderWidth: 1
      },
    {
        label: 'Percentage of Urgent Sitting Days',
        data: [<?php echo $percent_urgency_48; ?>, <?php echo $percent_urgency_49; ?>, <?php echo $percent_urgency_50; ?>, <?php echo $percent_urgency_51; ?>, <?php echo $percent_urgency_52; ?>, <?php echo $percent_urgency_53; ?>, <?php echo $percent_urgency_54; ?>],
        borderWidth: 1
      }
    ]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
</script>

 

 