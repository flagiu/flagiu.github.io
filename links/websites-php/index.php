<?php
$dataFile = 'data.txt';
$items = [];
$categories = [];

// Read data file
if (file_exists($dataFile)) {
    $lines = file($dataFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

    foreach ($lines as $line) {
        list($name, $description, $tags) = explode('|', $line);

        $tagArray = array_map('trim', explode(',', $tags));

        $items[] = [
            'name' => trim($name),
            'description' => trim($description),
            'tags' => $tagArray
        ];

        foreach ($tagArray as $tag) {
            $categories[$tag] = $tag;
        }
    }
}

sort($categories);

$selectedCategory = $_GET['category'] ?? '';
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Item List</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 30px auto;
            padding: 20px;
        }

        .filter {
            margin-bottom: 20px;
        }

        .item {
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }

        .tags {
            margin-top: 10px;
        }

        .tag {
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 3px 8px;
            margin-right: 5px;
            border-radius: 3px;
            font-size: 12px;
        }
    </style>
</head>
<body>

<h1>Items</h1>

<form method="get" class="filter">
    <label for="category">Filter by Category:</label>

    <select name="category" id="category" onchange="this.form.submit()">
        <option value="">All Categories</option>

        <?php foreach ($categories as $category): ?>
            <option value="<?= htmlspecialchars($category) ?>"
                <?= ($selectedCategory === $category) ? 'selected' : '' ?>>
                <?= htmlspecialchars($category) ?>
            </option>
        <?php endforeach; ?>
    </select>
</form>

<?php
$found = false;

foreach ($items as $item) {

    if (
        $selectedCategory &&
        !in_array($selectedCategory, $item['tags'])
    ) {
        continue;
    }

    $found = true;
    ?>

    <div class="item">
        <h2><?= htmlspecialchars($item['name']) ?></h2>

        <p><?= htmlspecialchars($item['description']) ?></p>

        <div class="tags">
            <?php foreach ($item['tags'] as $tag): ?>
                <span class="tag">
                    <?= htmlspecialchars($tag) ?>
                </span>
            <?php endforeach; ?>
        </div>
    </div>

    <?php
}

if (!$found) {
    echo "<p>No items found.</p>";
}
?>

</body>
</html>
