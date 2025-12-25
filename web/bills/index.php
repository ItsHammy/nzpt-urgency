<?php

// Load data from urgency.sqlite3
$db = new SQLite3('../urgency.sqlite3');
$num_days_sat = $db->querySingle('SELECT COUNT(id) FROM urgency');
$num_days_urgency = $db->querySingle('SELECT COUNT(id) FROM urgency WHERE in_urgency = 1');
$percent_urgency = $num_days_sat > 0 ? round(($num_days_urgency / $num_days_sat) * 100, 2) : 0;
$last_day_urgent = $db->querySingle('SELECT date FROM urgency WHERE in_urgency = 1 ORDER BY date DESC LIMIT 1');
$last_day_urgent_readable = $last_day_urgent ? (new DateTime($last_day_urgent))->format('d M Y') : 'N/A';
$days_since_urgency = $last_day_urgent ? (new DateTime())->diff(new DateTime($last_day_urgent))->days : 'N/A';
$last_updated = file_get_contents('../lastupdate.txt');
$count_bills_affected = $db->querySingle('SELECT COUNT(id) FROM bills');

?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The <?php echo $count_bills_affected; ?> bills passed under urgency - NZPT</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/modern-normalize/1.0.0/modern-normalize.min.css">
    <link rel="stylesheet" href="../assets/style.css">
    <link rel="icon" href="../assets/favicon.ico" type="image/x-icon">
    <script src="assets/script.js"></script>
    <!-- META TAGS -->
    <meta name="description" content="The 54th Parliament of New Zealand has passed <?php echo $count_bills_affected; ?> bills under urgency. View the full list of bills affected by urgency here.">
    <meta name="author" content="CJ Sandall">
    <!-- TWITTER CARD META -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:creator" content="@ohitshammy">
    <meta name="twitter:title" content="Urgency Bill Viewer - New Zealand Politics Tracker">
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
        <h5>View the <?php echo $count_bills_affected; ?> bills passed under urgency.</h5>
        <nav>
            <a href="../">Urgency Tracker</a>
            <a href="../bills" class="active">Bills Viewer</a>
            <a href="../historical">Historical Data</a>
            <a href="https://cjs.nz/socials" target="_blank">Contact</a>
        </nav>
    </header>
    <main class="bill-list">
    <h2>54th Parliament Bills (in part) Passed Under Urgency</h2>
    <p class="bill-list__note">
        <strong>Note:</strong> This does not mean all parts of the bill were under urgency, 
        but just one or more parts were. The description is taken from the NZ Parliament website and does not reflect the views of NZPT developers. Boxes marked in red have been manually adjusted.
    </p>

    <div class="bill-grid">
        <?php
        $results = $db->query('SELECT bill_name, url, mps, desc FROM bills ORDER BY bill_name ASC');
        while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
            $name = htmlspecialchars($row['bill_name']);
            $mps = htmlspecialchars($row['mps']);
            $desc = htmlspecialchars($row['desc']);
            $url  = htmlspecialchars($row['url']);
        ?>
            <article class="bill-card">
                <h3 class="bill-card__title"><?php echo $name; ?></h3>
                <p class="bill-card__mps"> <i class="fa-solid fa-person"></i> <?php echo $mps; ?></p>
                <p class="bill-card__meta"><?php echo $desc; ?></p>
                <a href="<?php echo $url; ?>" 
                   class="bill-card__link" 
                   target="_blank" 
                   rel="noopener noreferrer">
                    View Bill
                </a>
            </article>
        <?php } ?>
        <article class="bill-card__adjusted">
            <h3 class="bill-card__title">Report an Issue</h3>
            <p class="bill-card__meta">If there is any issues with the information provided please report the issue on Github, or by emailing me.</p>
            <a href="https://github.com/itshammy/nzpt-urgency/issues" 
                class="bill-card__link" 
                target="_blank" 
                rel="noopener noreferrer">
                Report on GitHub
            </a>
            <a href="mailto:cj@cjs.nz" 
                class="bill-card__link" 
                target="_blank" 
                rel="noopener noreferrer">
                Email Me
            </a>
        </article>
    </div>
    </main>
    <footer>
        <p>Data is sourced from the <a href="https://www.parliament.nz/en" target="_blank">New Zealand Parliament website</a>. | View the Source Code on <a href="https://github.com/itshammy/nzpt-urgency" target="_blank">GitHub</a>.</p>
        <p>Created by <a href="https://cjs.nz">CJ</a>.<br><a href="https://www.buymeacoffee.com/hammy"><img width="10%" src="https://img.buymeacoffee.com/button-api/?text=Buy me a Latte&emoji=☕&slug=hammy&button_colour=BD5FFF&font_colour=ffffff&font_family=Poppins&outline_colour=000000&coffee_colour=FFDD00" /></a></p>
    </footer>
</body>
