<?php
error_reporting(E_ALL & ~E_NOTICE);
ini_set('display_errors', TRUE);
ini_set('display_startup_errors', TRUE);
include_once('db.php');
include_once('csrf.php');
#session_start();
#session_regenerate_id();
$direction = "*";
$networkType = "*";
$variant = "*";

$db = ierg4210_DB();
parse_str($_SERVER['QUERY_STRING']);
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
					<li class="active"><a href="MainPage.php">Home</a></li>
					<li><a href="Admin.php">Admin Page</a></li>
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
		  		<h4>Please Select a Network Source: <b><u><i><?php echo $networkType ?></i></u></b></h4>
						<?php
								$q = 'SELECT ID, Network FROM [Network_List]';
								$result = $db->prepare($q);
								$result->execute();
								$Network = $result->fetchAll(PDO::FETCH_ASSOC);
								for ($i = 0; $i < count($Network); $i++){
										echo '<button type "button"><a href="?networkType=' .$Network[$i]['Network']. '&direction=' .$direction. '&variant=' .$variant. '">'. $Network[$i]['Network']. '</a></button>';
								}
						?>
						<h4>Please Select a Direction (uplink/downlink): <b><u><i><?php echo $direction ?></i></u></b></h4>
						<?php
								$q = 'SELECT ID, Direction FROM [Direction_List]';
								$result = $db->prepare($q);
								$result->execute();
								$Direction = $result->fetchAll(PDO::FETCH_ASSOC);
								for ($i = 0; $i < count($Direction); $i++){
										echo '<button type "button"><a href="?networkType=' .$networkType. '&direction=' .$Direction[$i]['Direction']. '&variant=' .$variant. '">'.$Direction[$i]['Direction'].  '</a></button>';
								}
						?>
            <h4>Please Select a Variant: <b><u><i><?php echo $variant ?></i></u></b></h4>
            <?php
                $q = 'SELECT ID, Variant FROM [Variant_List]';
                $result = $db->prepare($q);
                $result->execute();
                $Variant = $result->fetchAll(PDO::FETCH_ASSOC);
                for ($i = 0; $i < count($Variant); $i++){
                    echo '<button type "button"><a href="?networkType=' .$networkType. '&direction=' .$direction. '&variant=' .$Variant[$i]['Variant']. '">'.$Variant[$i]['Variant']. '</a></button>';
                }
            ?>
		  	</div>
			</div>

      <div class="panel panel-info">
		  	<div class="panel-heading">Time Graph</div>
		  	<div class="panel-body">
          <?php
            if ($networkType != "*" && $direction != "*" && $variant != "*")
              echo
              '<label> Select Start/End Time ("YYYY_MM_DD_HH", e.g. 2020_09_15_12) </label>
                  <form id = "TimeSelect" method= "GET" action="../cgi-bin/draw_graph.py" enctype="multipart/form-data">
                  <input id= "operation" type="hidden" name= "operation" value="draw_graph", required="true" />
                  <input id= "network" type="hidden" name= "network" value="'  .$networkType. '", required="true" />
                  <input id= "direction" type="hidden" name= "direction" value="'  .$direction. '", required="true" />
                  <input id= "variant" type="hidden" name= "variant" value="'  .$variant. '", required="true" />
                  <label> Start </label>
                  <input id= "start_time" type="text" name= "start_time" required="true" />
                  <label> End </label>
                  <input id= "end_time" type="text" name= "end_time" required="true" />
                  <br/>
                  <label> Select Scale </label>
                  <br/>
                  <input id= "scale" type="text" name= "scale" pattern="^[0-9]*$" />
                  <input type= "submit" value="Submit" />
              </form>';
           ?>
				</div>
			</div>

			<div class="panel panel-info">
		  	<div class="panel-heading">Trace List</div>
		  	<div class="panel-body">
					<table class="table table-bordered">
						<thead>
		 					<tr>
			 					<th>Network</th>
			 					<th>Direction</th>
								<th>Variant</th>
			 					<th>Trace Name</th>
			 					<th>Upload Time</th>
		 					</tr>
						</thead>
						<tbody>
							<?php
							if($networkType != null && $direction != null){
								$q = 'SELECT ID, Network, Direction, Variant, Trace_Name, Upload_Time FROM [Trace] WHERE Network = (?) and Direction = (?) and Variant = (?)';
								$result = $db->prepare($q);
								$result->execute(array($networkType, $direction, $variant));
								$Trace = $result->fetchAll(PDO::FETCH_ASSOC);
								for ($i = 0; $i < count($Trace); $i++){
									echo '<tr>';
									echo '<td>'. $Trace[$i]['Network'] .'</td>';
									echo '<td>'. $Trace[$i]['Direction'] .'</td>';
									echo '<td>'. $Trace[$i]['Variant'] .'</td>';
									echo '<td><a href = "../trace/' .$Trace[$i]['Network']. '/' .$Trace[$i]['Direction']. '/' .$Trace[$i]['Variant']. '/' .$Trace[$i]['Trace_Name'].'">'. $Trace[$i]['Trace_Name'] .'</a></td>';
									echo '<td>'. $Trace[$i]['Upload_Time'] .'</td>';
									echo '</tr>';
								}
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
