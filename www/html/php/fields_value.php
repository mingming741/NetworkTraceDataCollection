<?php
error_reporting(E_ALL & ~E_NOTICE);
ini_set('display_errors', TRUE);
ini_set('display_startup_errors', TRUE);
include_once('db.php');
parse_str($_SERVER['QUERY_STRING']);

$db = ierg4210_DB();
if ($field == "Network"){
  $q = 'SELECT ID, Network FROM [Network_List]';
  $result = $db->prepare($q);
  $result->execute();
  $array = $result->fetchAll(PDO::FETCH_ASSOC);
  echo json_encode($array);
}
if ($field == "Variant"){
  $q = 'SELECT ID, Variant FROM [Variant_List]';
  $result = $db->prepare($q);
  $result->execute();
  $array = $result->fetchAll(PDO::FETCH_ASSOC);
  echo json_encode($array);
}
if ($field == "Direction"){
  $q = 'SELECT ID, Direction FROM [Direction_List]';
  $result = $db->prepare($q);
  $result->execute();
  $array = $result->fetchAll(PDO::FETCH_ASSOC);
  echo json_encode($array);
}


header('Content-Type: application/json');
?>
