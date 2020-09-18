<?php
include_once('db.php');


function ierg4210_make_dir() {
	target_dir = $_POST['target_dir'];
	if (!file_exists(target_dir)) {
		mkdir(target_dir, 0777, true);
	}
	return 0;
}


header('Content-Type: application/json');
// input validation
if (empty($_REQUEST['action']) || !preg_match('/^\w+$/', $_REQUEST['action'])) {
	echo json_encode(array('failed'=>'undefined'));
	exit();
}

try {
	$returnVal = call_user_func('ierg4210_' . $_REQUEST['action'])
}
catch(Exception $e) {
	echo 'while(1);' . json_encode(array('failed' => $e->getMessage()));
}
?>
