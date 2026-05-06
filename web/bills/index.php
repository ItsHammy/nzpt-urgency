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
$allBills = $db->query('SELECT tags, mps FROM bills');
$tagCounts = [
    'PUU'  => 0, // Passed
    'NP'   => 0, // Voted Down
    'AV'   => 0, // Awaiting Vote
    'MB'   => 0, // Money Bill
    'NMB'  => 0, // Non-Money Bill
];
$mpCounts = [];
while ($row = $allBills->fetchArray(SQLITE3_ASSOC)) {
    // Tags
    $tags = array_filter(array_map('trim', explode(',', $row['tags'] ?? '')));
    foreach ($tags as $tag) {
        if (isset($tagCounts[$tag])) {
            $tagCounts[$tag]++;
        }
    }
    // MPs — split by comma, count each
    $mps = array_filter(array_map('trim', explode(',', $row['mps'] ?? '')));
    foreach ($mps as $mp) {
        if ($mp === '') continue;
        $mpCounts[$mp] = ($mpCounts[$mp] ?? 0) + 1;
    }
}

// Top 3 MPs
arsort($mpCounts);
$top3MPs = array_slice($mpCounts, 0, 3, true);
$top3MPLabels = json_encode(array_keys($top3MPs));
$top3MPValues = json_encode(array_values($top3MPs));

// Status chart data
$statusLabels = json_encode(['Passed', 'Voted Down', 'Awaiting Vote']);
$statusValues = json_encode([$tagCounts['PUU'], $tagCounts['NP'], $tagCounts['AV']]);

// Money chart data
$moneyLabels = json_encode(['Money Bills', 'Non-Money Bills']);
$moneyValues = json_encode([$tagCounts['MB'], $tagCounts['NMB']]);

?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The <?php echo $count_bills_affected; ?> bills seen under urgency - NZPT</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/modern-normalize/1.0.0/modern-normalize.min.css">
    <link rel="stylesheet" href="../assets/style.css">
    <link rel="icon" href="../assets/favicon.ico" type="image/x-icon">
    <script src="assets/script.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
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
        <h5>View the <?php echo $count_bills_affected; ?> bills seen under urgency.</h5>
        <nav>
            <a href="../">Urgency Tracker</a>
            <a href="../bills" class="active">Bills Viewer</a>
            <a href="../historical">Historical Data</a>
            <a href="https://nzpt.cjs.nz">NZPT Home</a>
            <a href="https://cjs.nz/socials" target="_blank">Contact</a>
        </nav>
    </header>
    <?php if (isset($_GET['oldurl']) && $_GET['oldurl'] == 'true'): ?>
            <div class="alert">
                <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span>
                <p><strong>Notice:</strong> <em>NZPolToolbox now has more than just this Urgency Tracker.</em> You have been automatically redirected to the new URL for this tool. The old URLs will not work in the future. Please update your bookmarks! <br><i class="fa-solid fa-heart"></i> Thank you for your continued support!</p>
            </div>
        <?php endif; ?>
    <main class="bill-list">
    <h2>54th Parliament Bills seen Under Urgency</h2>
    <p class="bill-list__note">
        <strong>Note:</strong> This does not mean all parts of the bill were under urgency, 
        but just one or more parts were. The description is taken from the NZ Parliament website and does not reflect the views of NZPT developers. Boxes marked in red have been manually adjusted.
    </p>
    <!-- Live Patch: Notice that the tool has stopped working. -->
    <div class="alert">
        <span class="closebtn" onclick="this.parentElement.style.display='none';">&times;</span>
        <strong>Notice:</strong> A recent change to the Parliament website has meant that some bill details have not correctly been scraped. I am working on a fix to this. Thank you for your patience and understanding. <i class="fa-solid fa-heart"></i>
    </div>
    <!-- End Live Patch -->

    <!-- ===== QUICKSTATS SECTION ===== -->
    <section class="quickstats">
        <h2 class="quickstats__heading">Quick Stats</h2>
        <div class="quickstats__grid">

            <!-- Top 3 MPs -->
            <div class="quickstats__card">
                <h3 class="quickstats__card-title">
                    <i class="fa-solid fa-ranking-star"></i> Top MPs by Bills
                </h3>
                <div class="quickstats__chart-wrap">
                    <canvas id="chart-mps" aria-label="Top 3 MPs by number of bills" role="img"></canvas>
                </div>
            </div>

            <!-- Bill Status -->
            <div class="quickstats__card">
                <h3 class="quickstats__card-title">
                    <i class="fa-solid fa-chart-pie"></i> Bill Outcomes
                </h3>
                <div class="quickstats__chart-wrap quickstats__chart-wrap--doughnut">
                    <canvas id="chart-status" aria-label="Bill outcomes breakdown" role="img"></canvas>
                </div>
            </div>

            <!-- Money vs Non-Money -->
            <div class="quickstats__card">
                <h3 class="quickstats__card-title">
                    <i class="fa-solid fa-scale-balanced"></i> Money vs Non-Money
                </h3>
                <div class="quickstats__chart-wrap quickstats__chart-wrap--doughnut">
                    <canvas id="chart-money" aria-label="Money bills vs non-money bills" role="img"></canvas>
                </div>
            </div>

        </div>
    </section>
    <!-- ===== END QUICKSTATS ===== -->

    <div class="sorting-centre">
        <?php 
        $sort = $_GET['sort'] ?? 'default';

        switch ($sort) {
            case 'mp':
                $orderBy = 'mps ASC';
                break;
            case 'name_asc':
                $orderBy = 'bill_name ASC';
                break;
            case 'name_desc':
                $orderBy = 'bill_name DESC';
                break;
            case 'default':
            default:
                $orderBy = 'rowid DESC';
                break;
        }
        ?>
        <form method="GET" class="searchbox">
            <input 
                type="text"
                name="q" 
                placeholder="Search the <?php echo $count_bills_affected ?> bills by Name, MPs, or keywords..." 
                value="<?= htmlspecialchars($_GET['search'] ?? '') ?>"
            >
            <button type="submit">Search</button>
        </form>
        <form method="GET">
            <select name="sort" id="sort" onchange="this.form.submit()">
                <option value="default" <?= $sort === 'default' ? 'selected' : '' ?>>Default (Recent)</option>
                <option value="mp" <?= $sort === 'mp' ? 'selected' : '' ?>>MP</option>
                <option value="name_asc" <?= $sort === 'name_asc' ? 'selected' : '' ?>>Name (A–Z)</option>
                <option value="name_desc" <?= $sort === 'name_desc' ? 'selected' : '' ?>>Name (Z–A)</option>
            </select>
        </form>
    </div>

    <div class="bill-grid">
        <?php
        $tagMap = [
            'PUU'  => ['label' => 'Passed', 'class' => 'tag--passed'],
            'NP'   => ['label' => 'Voted Down', 'class' => 'tag--failed'],
            'SKU'  => ['label' => 'Skipped Committee', 'class' => 'tag--skipped'],
            'AV'   => ['label' => 'Awaiting Vote', 'class' => 'tag--awaiting'],
            'MB'   => ['label' => 'Money Bill', 'class' => 'tag--money'],
            'NMB'  => ['label' => 'Non-Money Bill', 'class' => 'tag--nonmoney'],
            'AMP'  => ['label' => 'Amendment Paper', 'class' => 'tag--amendment'],
            'BPUM' => ['label' => 'Bipartisan Urgency', 'class' => 'tag--bipartisan'],
        ];
        $search = $_GET['q'] ?? '';
        $search = trim($search);
        $sql = "SELECT bill_name, tags, url, mps, desc FROM bills";

        if ($search !== '') {
            $safeSearch = SQLite3::escapeString($search);
            $sql .= " WHERE bill_name LIKE '%$safeSearch%' 
                      OR mps LIKE '%$safeSearch%' 
                      OR desc LIKE '%$safeSearch%'";
        }
        
        $sql .= " ORDER BY $orderBy";
        
        $results = $db->query($sql);
        while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
            $name = htmlspecialchars($row['bill_name']);
            $mps = htmlspecialchars($row['mps']);
            $desc = htmlspecialchars($row['desc']);
            $url  = htmlspecialchars($row['url']);
            $tagsRaw = $row['tags'] ?? '';
            $tags = array_filter(array_map('trim', explode(',', $tagsRaw)));
        ?>
            <article class="bill-card">
                <h3 class="bill-card__title"><?php echo $name; ?></h3>
                <?php if (!empty($tags)) { ?>
                    <div class="bill-card__tags">
                        <?php foreach ($tags as $tagCode) {
                            if (isset($tagMap[$tagCode])) {
                                $tag = $tagMap[$tagCode];
                        ?>
                            <span class="tag <?= $tag['class'] ?>">
                                <?= htmlspecialchars($tag['label']) ?>
                            </span>
                        <?php 
                            }
                        } ?>
                    </div>
                <?php } ?>
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

<script>
// ── Shared Chart.js defaults ──────────────────────────────────────────────
Chart.defaults.font.family = "system-ui, -apple-system, 'Segoe UI', sans-serif";
Chart.defaults.color = "#555";

// ── 1. Top 3 MPs – Horizontal Bar ────────────────────────────────────────
(function () {
    const labels = <?php echo $top3MPLabels; ?>;
    const values = <?php echo $top3MPValues; ?>;
    if (!labels.length) return;

    new Chart(document.getElementById('chart-mps'), {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Bills',
                data: values,
                backgroundColor: ['#2563eb', '#7c3aed', '#0891b2'],
                borderRadius: 6,
                borderSkipped: false,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.parsed.x} bill${ctx.parsed.x !== 1 ? 's' : ''}`
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, precision: 0 },
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                y: {
                    grid: { display: false }
                }
            }
        }
    });
})();

// ── 2. Bill Outcomes – Doughnut ──────────────────────────────────────────
(function () {
    const labels = <?php echo $statusLabels; ?>;
    const values = <?php echo $statusValues; ?>;

    new Chart(document.getElementById('chart-status'), {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: ['#16a34a', '#dc2626', '#0284c7'],
                borderWidth: 2,
                borderColor: '#fff',
                hoverOffset: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '62%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 14, boxWidth: 12, borderRadius: 3 }
                },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.label}: ${ctx.parsed} bill${ctx.parsed !== 1 ? 's' : ''}`
                    }
                }
            }
        }
    });
})();

// ── 3. Money vs Non-Money – Doughnut ─────────────────────────────────────
(function () {
    const labels = <?php echo $moneyLabels; ?>;
    const values = <?php echo $moneyValues; ?>;

    new Chart(document.getElementById('chart-money'), {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: ['#7c3aed', '#f59e0b'],
                borderWidth: 2,
                borderColor: '#fff',
                hoverOffset: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '62%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 14, boxWidth: 12, borderRadius: 3 }
                },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.label}: ${ctx.parsed} bill${ctx.parsed !== 1 ? 's' : ''}`
                    }
                }
            }
        }
    });
})();
</script>
</body>