<?php
error_reporting(E_ALL & ~E_NOTICE);
ini_set('display_errors', TRUE);
ini_set('display_startup_errors', TRUE);
include_once('db.php');
include_once('csrf.php');
#session_start();
#session_regenerate_id();

$db = ierg4210_DB();
parse_str($_SERVER['QUERY_STRING']);
$networkType = null;
$direction = null;
?>


<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="../../favicon.ico">
	<title>Network Data collection | mclab, CUHK IE</title>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
    <link href="theme.css" rel="stylesheet">
  </head>


  <body>
	  <div class="navbar-wrapper">
		  <div class="container">
		  <nav class="navbar navbar-inverse">
			<div class="container">
			  <div class="navbar-header">
				<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target=".navbar-collapse">
				  <span class="sr-only">Toggle navigation</span>
				  <span class="icon-bar"></span>
				  <span class="icon-bar"></span>
				  <span class="icon-bar"></span>
				</button>
				<a class="navbar-brand" href="MainPage.php">Trace</a>
			  </div>
			  <div class="navbar-collapse collapse">
				<ul class="nav navbar-nav">
					<li><a href="MainPage.php">Home</a></li>
					<li class="active"><a href="Admin.php">Admin Page</a></li>
				</ul>
			  </div><!--/.nav-collapse -->
			</div>
		  </nav>
		  </div>
	  </div>

		<div class="container theme-showcase" role="main">
	  	<div class="panel panel-info">
		  	<div class="panel-heading">Source Selection</div>
		  	<div class="panel-body">
		  		<h4>Operations</h4>
            <div>
              <button type "button" ><a href="?opid=0"> Upload Record</a></button>
              <button type "button" ><a href="?opid=1"> Add Network</a></button>
              <button type "button" ><a href="?opid=2"> Add Variant</a></button>
              <button type "button" ><a href="?opid=3"> Delete Network</a></button>
              <button type "button" ><a href="?opid=4"> Delete Variant</a></button>
            </div>
            <div>
              <?php
                if($opid == 0){
                    echo
                    '<label> Upload Record </label>
                        <form id = "Upload_Record" method= "POST" action="handler.php?action=Upload_Record" enctype="multipart/form-data">
                        <select name = "Network_ID" id = "Network_ID">';
                          $q = 'SELECT ID, Network FROM [Network_List]';
                          $result = $db->prepare($q);
                          $result->execute();
                          $array = $result->fetchAll(PDO::FETCH_ASSOC);
                          for ($i = 0; $i < count($array); $i++){
                             echo "<option value =" .$array[$i]['ID']. ">" .$array[$i]['Network']. "</option>";
                          }
                          echo'</select>
                          <select name = "Direction_ID" id = "Direction_ID">';
                            $q = 'SELECT ID, Direction FROM [Direction_List]';
                            $result = $db->prepare($q);
                            $result->execute();
                            $array = $result->fetchAll(PDO::FETCH_ASSOC);
                            for ($i = 0; $i < count($array); $i++){
                               echo "<option value =" .$array[$i]['ID']. ">" .$array[$i]['Direction']. "</option>";
                            }
                            echo'</select>
                          <select name = "Variant_ID" id = "Variant_ID">';
                            $q = 'SELECT ID, Variant FROM [Variant_List]';
                            $result = $db->prepare($q);
                            $result->execute();
                            $array = $result->fetchAll(PDO::FETCH_ASSOC);
                            for ($i = 0; $i < count($array); $i++){
                               echo "<option value =" .$array[$i]['ID']. ">" .$array[$i]['Variant']. "</option>";
                            }
                            echo'</select>
                        <input type = "file" name= "file" required= "true" accept="text/txt" />
                        <input type= "submit" value="Submit" />
                    </form>';
                }
                if($opid == 1){
                    echo
                    '<label> Add Network </label>
                        <form id = "Add_Network" method= "POST" action="handler.php?action=Add_Network">
                        <input id= "Network" type="text" name= "Network" required="true" pattern="^[\w\- ]+$" />
                        <input type= "submit" value="Submit" />
                    </form>';
                }
                if($opid == 2){
                    echo
                    '<label> Add Variant </label>
                        <form id = "Add_Variant" method= "POST" action="handler.php?action=Add_Variant">
                        <input id= "Variant" type="text" name= "Variant" required="true" pattern="^[\w\- ]+$" />
                        <input type= "submit" value="Submit" />
                    </form>';
                }
                if($opid == 3){
                    echo
                    '<label> Delete Network </label>
                        <form id = "Delete_Network" method= "POST" action="handler.php?action=Delete_Network">
                        <select name = "Network_ID" id = "Network_ID">';
                          $q = 'SELECT ID, Network FROM [Network_List]';
                          $result = $db->prepare($q);
                          $result->execute();
                          $array = $result->fetchAll(PDO::FETCH_ASSOC);
                          for ($i = 0; $i < count($array); $i++){
                             echo "<option value =" .$array[$i]['ID']. ">" .$array[$i]['Network']. "</option>";
                          }
                          echo'</select>
                        <input type= "submit" value="Submit" />
                    </form>';
                }
                if($opid == 4){
                    echo
                    '<label> Delete Variant </label>
                        <form id = "Delete_Variant" method= "POST" action="handler.php?action=Delete_Variant">
                        <select name = "Variant_ID" id = "Variant_ID">';
                          $q = 'SELECT ID, Variant FROM [Variant_List]';
                          $result = $db->prepare($q);
                          $result->execute();
                          $array = $result->fetchAll(PDO::FETCH_ASSOC);
                          for ($i = 0; $i < count($array); $i++){
                             echo "<option value =" .$array[$i]['ID']. ">" .$array[$i]['Variant']. "</option>";
                          }
                          echo'</select>
                        <input type= "submit" value="Submit" />
                    </form>';
                }
              ?>
            </div>
		  	</div>
			</div>

			<div class="panel panel-info">
		  	<div class="panel-heading">Network List</div>
		  	<div class="panel-body">
					<table class="table table-bordered">
						<thead>
		 					<tr>
			 					<th>ID</th>
			 					<th>Network</th>
		 					</tr>
						</thead>
						<tbody>
							<?php
								$q = 'SELECT ID, Network FROM [Network_List]';
								$result = $db->prepare($q);
								$result->execute();
								$Trace = $result->fetchAll(PDO::FETCH_ASSOC);
								for ($i = 0; $i < count($Trace); $i++){
									echo '<tr>';
                  echo '<td>'. $Trace[$i]['ID'] .'</td>';
									echo '<td>'. $Trace[$i]['Network'] .'</td>';
									echo '</tr>';
								}
							?>
						</tbody>
					</table>
		  	</div>
			</div>

      <div class="panel panel-info">
		  	<div class="panel-heading">Direction List</div>
		  	<div class="panel-body">
					<table class="table table-bordered">
						<thead>
		 					<tr>
			 					<th>ID</th>
			 					<th>Direction</th>
		 					</tr>
						</thead>
						<tbody>
							<?php
								$q = 'SELECT ID, Direction FROM [Direction_List]';
								$result = $db->prepare($q);
								$result->execute();
								$Trace = $result->fetchAll(PDO::FETCH_ASSOC);
								for ($i = 0; $i < count($Trace); $i++){
									echo '<tr>';
                  echo '<td>'. $Trace[$i]['ID'] .'</td>';
									echo '<td>'. $Trace[$i]['Direction'] .'</td>';
									echo '</tr>';
								}
							?>
						</tbody>
					</table>
		  	</div>
			</div>


      <div class="panel panel-info">
		  	<div class="panel-heading">Variant List</div>
		  	<div class="panel-body">
					<table class="table table-bordered">
						<thead>
		 					<tr>
			 					<th>ID</th>
			 					<th>Variant</th>
		 					</tr>
						</thead>
						<tbody>
							<?php
								$q = 'SELECT ID, Variant FROM [Variant_List]';
								$result = $db->prepare($q);
								$result->execute();
								$Trace = $result->fetchAll(PDO::FETCH_ASSOC);
								for ($i = 0; $i < count($Trace); $i++){
									echo '<tr>';
                  echo '<td>'. $Trace[$i]['ID'] .'</td>';
									echo '<td>'. $Trace[$i]['Variant'] .'</td>';
									echo '</tr>';
								}
							?>
						</tbody>
					</table>
		  	</div>
			</div>

		</div>

		<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
		<script src="js/bootstrap.min.js"></script>
	</body>
</html>
