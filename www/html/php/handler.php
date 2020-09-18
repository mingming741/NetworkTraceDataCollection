<?php
error_reporting(E_ALL & ~E_NOTICE);
include_once('db.php');

function ierg4210_Add_Network() {
	if (!preg_match('/^[\w\-, ]+$/', $_POST['Network'])){
		throw new Exception("invalid-name");
	}
	global $db;
	$db = ierg4210_DB();
	if (!file_exists('../trace/' .$_POST['Network'])) {
		mkdir('../trace/' .$_POST['Network'], 0777, true);
	}
	$q = 'SELECT ID, Direction FROM [Direction_List]';
	$result = $db->prepare($q);
	$result->execute();
	$Direction = $result->fetchAll(PDO::FETCH_ASSOC);
	for ($i = 0; $i < count($Direction); $i++){
		if (!file_exists('../trace/' .$_POST['Network']. '/' .$Direction[$i]['Direction'])) {
			mkdir('../trace/' .$_POST['Network']. '/' .$Direction[$i]['Direction'], 0777, true);
		}
	}
	$q = $db->prepare("INSERT INTO [Network_List] (Network) VALUES (?)");
	return $q->execute(array($_POST['Network']));
}

function ierg4210_Add_Variant() {
	if (!preg_match('/^[\w\-, ]+$/', $_POST['Variant'])){
		throw new Exception("invalid-name");
	}
	global $db;
	$db = ierg4210_DB();
	$q = $db->prepare("INSERT INTO [Variant_List] (Variant) VALUES (?)");
	return $q->execute(array($_POST['Variant']));
}

function ierg4210_Delete_Network() {
	$net_id = (int) $_POST['Network_ID'];
	global $db;
	$db = ierg4210_DB();
	$q = $db->prepare("DELETE FROM [Network_List] WHERE ID = ?");
	return $q->execute(array($net_id));
}

function ierg4210_Delete_Variant() {
	$v_id = (int) $_POST['Variant_ID'];
	global $db;
	$db = ierg4210_DB();
	$q = $db->prepare("DELETE FROM [Variant_List] WHERE ID = ?");
	return $q->execute(array($v_id));
}

function ierg4210_Upload_Record() {
	$net_id = (int) $_POST['Network_ID'];
	$v_id = (int) $_POST['Variant_ID'];
	$d_id = (int) $_POST['Direction_ID'];
	global $db;
	$db = ierg4210_DB();
	$result = $db->prepare('SELECT ID, Direction FROM [Direction_List] WHERE ID = ?');
	$result->execute(array($d_id));
	$result = $result->fetchAll(PDO::FETCH_ASSOC);
	if (count($result) != 0) {
		$direction = $result[0]["Direction"];
	} else {
		exit();
	}
	$result = $db->prepare('SELECT ID, Network FROM [Network_List] WHERE ID = ?');
	$result->execute(array($net_id));
	$result = $result->fetchAll(PDO::FETCH_ASSOC);
	if (count($result) != 0){
		$network = $result[0]["Network"];
	} else {
		exit();
	}
	$result = $db->prepare('SELECT ID, Variant FROM [Variant_List] WHERE ID = ?');
	$result->execute(array($v_id));
	$result = $result->fetchAll(PDO::FETCH_ASSOC);
	if (count($result) != 0){
		$variant = $result[0]["Variant"];
	} else {
		exit();
	}
	#$target_file_directory = "../trace/".$network."/".$direction."/".$variant."/".$_FILES['file']['name'];
	$target_file_directory = "../trace/".$network."/".$direction."/".$variant;
	if (!file_exists($target_file_directory)) {
		mkdir($target_file_directory, 0777, true);
	}
	$target_file = $target_file_directory."/".$_FILES['file']['name'];
	if ($_FILES["file"]["error"] == 0) {
		if(!move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)){
				return 0;
		}
	}
	$uploadTime = date("Y/M/d, h:i:s A");
	$result = $db->prepare("INSERT INTO [Trace] (Network, Direction, Variant, Trace_Name, Upload_Time) VALUES (?, ?, ?, ?, ?)");
	return $result->execute(array($network, $direction, $variant, $_FILES['file']['name'], $uploadTime));
}


header('Content-Type: application/json');
// input validation
if (empty($_REQUEST['action']) || !preg_match('/^\w+$/', $_REQUEST['action'])) {
	echo json_encode(array('failed'=>'undefined'));
	exit();
}

try {
	if (($returnVal = call_user_func('ierg4210_' . $_REQUEST['action'])) === false) {
		if ($db && $db->errorCode()){
			error_log(print_r($db->errorInfo(), true));
		}
	}
	echo json_encode(array('success' => $returnVal));

} catch(PDOException $e) {
	error_log($e->getMessage());
	echo json_encode(array('failed'=>'error-db'));
} catch(Exception $e) {
	echo json_encode(array('failed' => $e->getMessage()));
}
?>
