<?php
	include 'JWT.php';

	$fo_realm = "demo";				// Real realm goes here
	$fo_key = "";					// Real key goes here
	$fo_channel = str_replace(' ', '+', $_GET["channel"]); // Restore +'s
	$fo_message = $_POST["data"];
	$fo_api_url = "http://api.fanout.io/realm/demo/publish/".$fo_channel.'/';
	$fo_headers = array("Content-Type: application/json");

	$rv = "";	// Return value to the browser

	// Generate the JSON Web Token if not in anonymous mode
	if(strlen($fo_key) > 0) {
		$claim = array('iss' => $fo_realm, 'exp' => time() + 3600);
		$token = JWT::encode($claim, base64_decode($fo_key));
		array_unshift($fo_headers, "Authorization: Bearer ".$token);
	}

	// Publish to Fanout using the REST API
	if(in_array('curl', get_loaded_extensions())) {
		// Use curl
		$curl_post = curl_init();
		curl_setopt($curl_post, CURLOPT_URL, $fo_api_url);
		curl_setopt($curl_post, CURLOPT_HTTPHEADER, $fo_headers);
		curl_setopt($curl_post, CURLOPT_POST, true);
		curl_setopt($curl_post, CURLOPT_POSTFIELDS, $fo_message);
		$rv = curl_exec($curl_post);
		$error = curl_error($curl_post);
		if($error != "") {
			$rv = $error;
		}
		else {
			$header_size = curl_getinfo($curl_post, CURLINFO_HEADER_SIZE);
			$rv = substr($rv, $header_size);
		}
		curl_close($curl_post);
	}
	else {
		// Use file_get_contents
		$opts = array(
			'http' => array(
				'method' => 'POST',
				'header' => $fo_headers,
				'content' => $fo_message
			)
		);
		$context = stream_context_create($opts);
		$rv = file_get_contents($fo_api_url, false, $context);
	}
	echo $rv;
?>
