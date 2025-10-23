<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    // Validate required fields
    if (!isset($input['playbook']) || !isset($input['status'])) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing required fields']);
        exit;
    }
    
    // Save to database or file
    $logEntry = [
        'id' => uniqid(),
        'playbook' => $input['playbook'],
        'status' => $input['status'],
        'time' => $input['time'] ?? 0,
        'hosts' => $input['hosts'] ?? 1,
        'timestamp' => $input['timestamp'] ?? date('c'),
        'tasks' => $input['tasks'] ?? [],
        'output' => $input['output'] ?? ''
    ];
    
    // Save to JSON file (or database)
    $logFile = 'logs/ansible_logs.json';
    $logs = file_exists($logFile) ? json_decode(file_get_contents($logFile), true) : [];
    $logs[] = $logEntry;
    file_put_contents($logFile, json_encode($logs, JSON_PRETTY_PRINT));
    
    echo json_encode(['success' => true, 'message' => 'Log saved successfully']);
} else {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
}
?>