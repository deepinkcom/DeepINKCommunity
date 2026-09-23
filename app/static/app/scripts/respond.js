/* NUGET: BEGIN LICENSE TEXT
 *
 * Microsoft grants you the right to use these script files for the sole
 * purpose of either: (i) interacting through your browser with the Microsoft
 * website or online service, subject to the applicable licensing or use
 * terms; or (ii) using the files as included with a Microsoft product subject
 * to that product's license terms. Microsoft reserves all other rights to the
 * files not expressly granted by Microsoft, whether by implication, estoppel
 * or otherwise. Insofar as a script file is dual licensed under GPL,
 * Microsoft neither took the code under GPL nor distributes it thereunder but
 * under the terms set out in this paragraph. All notices and licenses
 * below are for informational purposes only.
 *
 * NUGET: END LICENSE TEXT */
/*! matchMedia() polyfill - Test a CSS media type/query in JS. Authors & copyright (c) 2012: Scott Jehl, Paul Irish, Nicholas Zakas. Dual MIT/BSD license */
/*! NOTE: If you're already including a window.matchMedia polyfill via Modernizr or otherwise, you don't need this part */
window.matchMedia = window.matchMedia || (function(doc, undefined){
  
  var bool,
      docElem  = doc.documentElement,
      refNode  = docElem.firstElementChild || docElem.firstChild,
      // fakeBody required for <FF4 when executed in <head>
      fakeBody = doc.createElement('body'),
      div      = doc.createElement('div');
  
  div.id = 'mq-test-1';
  div.style.cssText = "position:absolute;top:-100em";
  fakeBody.style.background = "none";
  fakeBody.appendChild(div);
  
  return function(q){
    
    div.innerHTML = '&shy;<style media="'+q+'"> #mq-test-1 { width: 42px; }</style>';
    
    docElem.insertBefore(fakeBody, refNode);
    bool = div.offsetWidth == 42;  
    docElem.removeChild(fakeBody);
    
    return { matches: bool, media: q };
  };
  
})(document);




/*! Respond.js v1.2.0: min/max-width media query polyfill. (c) Scott Jehl. MIT/GPLv2 Lic. j.mp/respondjs  */
(function( win ){
	//exposed namespace
	win.respond		= {};
	
	//define update even in native-mq-supporting browsers, to avoid errors
	respond.update	= function(){};
	
	//expose media query support flag for external use
	respond.mediaQueriesSupported	= win.matchMedia && win.matchMedia( "only all" ).matches;
	
	//if media queries are supported, exit here
	if( respond.mediaQueriesSupported ){ return; }
	
	//define vars
	var doc 			= win.document,
		docElem 		= doc.documentElement,
		mediastyles		= [],
		rules			= [],
		appendedEls 	= [],
		parsedSheets 	= {},
		resizeThrottle	= 30,
		head 			= doc.getElementsByTagName( "head" )[0] || docElem,
		base			= doc.getElementsByTagName( "base" )[0],
		links			= head.getElementsByTagName( "link" ),
		requestQueue	= [],
		
		//loop stylesheets, send text content to translate
		ripCSS			= function(){
			var sheets 	= links,
				sl 		= sheets.length,
				i		= 0,
				//vars for loop:
				sheet, href, media, isCSS;

			for( ; i < sl; i++ ){
				sheet	= sheets[ i ],
				href	= sheet.href,
				media	= sheet.media,
				isCSS	= sheet.rel && sheet.rel.toLowerCase() === "stylesheet";

				//only links plz and prevent re-parsing
				if( !!href && isCSS && !parsedSheets[ href ] ){
					// selectivizr exposes css through the rawCssText expando
					if (sheet.styleSheet && sheet.styleSheet.rawCssText) {
						translate( sheet.styleSheet.rawCssText, href, media );
						parsedSheets[ href ] = true;
					} else {
						if( (!/^([a-zA-Z:]*\/\/)/.test( href ) && !base)
							|| href.replace( RegExp.$1, "" ).split( "/" )[0] === win.location.host ){
							requestQueue.push( {
								href: href,
								media: media
							} );
						}
					}
				}
			}
			makeRequests();
		},
		
		//recurse through request queue, get css text
		makeRequests	= function(){
			if( requestQueue.length ){
				var thisRequest = requestQueue.shift();
				
				ajax( thisRequest.href, function( styles ){
					translate( styles, thisRequest.href, thisRequest.media );
					parsedSheets[ thisRequest.href ] = true;
					makeRequests();
				} );
			}
		},
		
		//find media blocks in css text, convert to style blocks
		translate			= function( styles, href, media ){
			var qs			= styles.match(  /@media[^\{]+\{([^\{\}]*\{[^\}\{]*\})+/gi ),
				ql			= qs && qs.length || 0,
				//try to get CSS path
				href		= href.substring( 0, href.lastIndexOf( "/" )),
				repUrls		= function( css ){
					return css.replace( /(url\()['"]?([^\/\)'"][^:\)'"]+)['"]?(\))/g, "$1" + href + "$2$3" );
				},
				useMedia	= !ql && media,
				//vars used in loop
				i			= 0,
				j, fullq, thisq, eachq, eql;

			//if path exists, tack on trailing slash
			if( href.length ){ href += "/"; }	
				
			//if no internal queries exist, but media attr does, use that	
			//note: this currently lacks support for situations where a media attr is specified on a link AND
				//its associated stylesheet has internal CSS media queries.
				//In those cases, the media attribute will currently be ignored.
			if( useMedia ){
				ql = 1;
			}
			

			for( ; i < ql; i++ ){
				j	= 0;
				
				//media attr
				if( useMedia ){
					fullq = media;
					rules.push( repUrls( styles ) );
				}
				//parse for styles
				else{
					fullq	= qs[ i ].match( /@media *([^\{]+)\{([\S\s]+?)$/ ) && RegExp.$1;
					rules.push( RegExp.$2 && repUrls( RegExp.$2 ) );
				}
				
				eachq	= fullq.split( "," );
				eql		= eachq.length;
					
				for( ; j < eql; j++ ){
					thisq	= eachq[ j ];
					mediastyles.push( { 
						media	: thisq.split( "(" )[ 0 ].match( /(only\s+)?([a-zA-Z]+)\s?/ ) && RegExp.$2 || "all",
						rules	: rules.length - 1,
						hasquery: thisq.indexOf("(") > -1,
						minw	: thisq.match( /\(min\-width:[\s]*([\s]*[0-9\.]+)(px|em)[\s]*\)/ ) && parseFloat( RegExp.$1 ) + ( RegExp.$2 || "" ), 
						maxw	: thisq.match( /\(max\-width:[\s]*([\s]*[0-9\.]+)(px|em)[\s]*\)/ ) && parseFloat( RegExp.$1 ) + ( RegExp.$2 || "" )
					} );
				}	
			}

			applyMedia();
		},
        	
		lastCall,
		
		resizeDefer,
		
		// returns the value of 1em in pixels
		getEmValue		= function() {
			var ret,
				div = doc.createElement('div'),
				body = doc.body,
				fakeUsed = false;
									
			div.style.cssText = "position:absolute;font-size:1em;width:1em";
					
			if( !body ){
				body = fakeUsed = doc.createElement( "body" );
				body.style.background = "none";
			}
					
			body.appendChild( div );
								
			docElem.insertBefore( body, docElem.firstChild );
								
			ret = div.offsetWidth;
								
			if( fakeUsed ){
				docElem.removeChild( body );
			}
			else {
				body.removeChild( div );
			}
			
			//also update eminpx before returning
			ret = eminpx = parseFloat(ret);
								
			return ret;
		},
		
		//cached container for 1em value, populated the first time it's needed 
		eminpx,
		
		//enable/disable styles
		applyMedia			= function( fromResize ){
			var name		= "clientWidth",
				docElemProp	= docElem[ name ],
				currWidth 	= doc.compatMode === "CSS1Compat" && docElemProp || doc.body[ name ] || docElemProp,
				styleBlocks	= {},
				lastLink	= links[ links.length-1 ],
				now 		= (new Date()).getTime();

			//throttle resize calls	
			if( fromResize && lastCall && now - lastCall < resizeThrottle ){
				clearTimeout( resizeDefer );
				resizeDefer = setTimeout( applyMedia, resizeThrottle );
				return;
			}
			else {
				lastCall	= now;
			}
										
			for( var i in mediastyles ){
				var thisstyle = mediastyles[ i ],
					min = thisstyle.minw,
					max = thisstyle.maxw,
					minnull = min === null,
					maxnull = max === null,
					em = "em";
				
				if( !!min ){
					min = parseFloat( min ) * ( min.indexOf( em ) > -1 ? ( eminpx || getEmValue() ) : 1 );
				}
				if( !!max ){
					max = parseFloat( max ) * ( max.indexOf( em ) > -1 ? ( eminpx || getEmValue() ) : 1 );
				}
				
				// if there's no media query at all (the () part), or min or max is not null, and if either is present, they're true
				if( !thisstyle.hasquery || ( !minnull || !maxnull ) && ( minnull || currWidth >= min ) && ( maxnull || currWidth <= max ) ){
						if( !styleBlocks[ thisstyle.media ] ){
							styleBlocks[ thisstyle.media ] = [];
						}
						styleBlocks[ thisstyle.media ].push( rules[ thisstyle.rules ] );
				}
			}
			
			//remove any existing respond style element(s)
			for( var i in appendedEls ){
				if( appendedEls[ i ] && appendedEls[ i ].parentNode === head ){
					head.removeChild( appendedEls[ i ] );
				}
			}
			
			//inject active styles, grouped by media type
			for( var i in styleBlocks ){
				var ss		= doc.createElement( "style" ),
					css		= styleBlocks[ i ].join( "\n" );
				
				ss.type = "text/css";	
				ss.media	= i;
				
				//originally, ss was appended to a documentFragment and sheets were appended in bulk.
				//this caused crashes in IE in a number of circumstances, such as when the HTML element had a bg image set, so appending beforehand seems best. Thanks to @dvelyk for the initial research on this one!
				head.insertBefore( ss, lastLink.nextSibling );
				
				if ( ss.styleSheet ){ 
		        	ss.styleSheet.cssText = css;
		        } 
		        else {
					ss.appendChild( doc.createTextNode( css ) );
		        }
		        
				//push to appendedEls to track for later removal
				appendedEls.push( ss );
			}
		},
		//tweaked Ajax functions from Quirksmode
		ajax = function( url, callback ) {
			var req = xmlHttp();
			if (!req){
				return;
			}	
			req.open( "GET", url, true );
			req.onreadystatechange = function () {
				if ( req.readyState != 4 || req.status != 200 && req.status != 304 ){
					return;
				}
				callback( req.responseText );
			}
			if ( req.readyState == 4 ){
				return;
			}
			req.send( null );
		},
		//define ajax obj 
		xmlHttp = (function() {
			var xmlhttpmethod = false;	
			try {
				xmlhttpmethod = new XMLHttpRequest();
			}
			catch( e ){
				xmlhttpmethod = new ActiveXObject( "Microsoft.XMLHTTP" );
			}
			return function(){
				return xmlhttpmethod;
			};
		})();
	
	//translate CSS
	ripCSS();
	
	//expose update for re-running respond later on
	respond.update = ripCSS;
	
	//adjust on resize
	function callMedia(){
		applyMedia( true );
	}
	if( win.addEventListener ){
		win.addEventListener( "resize", callMedia, false );
	}
	else if( win.attachEvent ){
		win.attachEvent( "onresize", callMedia );
	}
})(this);

// SIG // Begin signature block
// SIG // MIIngQYJKoZIhvcNAQcCoIIncjCCJ24CAQExDzANBglg
// SIG // hkgBZQMEAgEFADB3BgorBgEEAYI3AgEEoGkwZzAyBgor
// SIG // BgEEAYI3AgEeMCQCAQEEEBDgyQbOONQRoqMAEEvTUJAC
// SIG // AQACAQACAQACAQACAQAwMTANBglghkgBZQMEAgEFAAQg
// SIG // w3y8PXLL3CtA/3Hg+8ZTHHP4KbtNHdPwcW38NSVz/yGg
// SIG // ggzeMIIGGTCCBAGgAwIBAgITMwAAAf3k91kxw2Tc4QAA
// SIG // AAAB/TANBgkqhkiG9w0BAQsFADBXMQswCQYDVQQGEwJV
// SIG // UzEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9u
// SIG // MSgwJgYDVQQDEx9NaWNyb3NvZnQgQ29kZSBTaWduaW5n
// SIG // IFBDQSAyMDI0MB4XDTI2MDQxNjE4NTg1MVoXDTI3MDQx
// SIG // NTE4NTg1MVowgYgxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
// SIG // EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4w
// SIG // HAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xMjAw
// SIG // BgNVBAMTKU1pY3Jvc29mdCAzcmQgUGFydHkgQXBwbGlj
// SIG // YXRpb24gQ29tcG9uZW50MIIBIjANBgkqhkiG9w0BAQEF
// SIG // AAOCAQ8AMIIBCgKCAQEAySyr5uf9sXckExv7VIrrr8Oq
// SIG // IRrb95I5+Ognua2kG0Q9rU80bzMLdSjaeKKjPOUaTswc
// SIG // fzSmqsxDkUlMBw/NsOS5lrR89dqEEtRg6WdJvwPVFiJf
// SIG // wOjYkgFFY7FZgfUnXcRyZ01b9mfi9a7Xnkp8HqGDGMXX
// SIG // D9HyNjP9KoKrdORqrkHOCNDFqyF/zEKbye9S5tvmom3B
// SIG // G1IhObqlRZYYhFqANjNv1ogX4zJEll7Nk5u5awit9+e5
// SIG // FzxqeqrXFhyyAbWZoY39txBUIjsabUX7F5hiF1qLqLV1
// SIG // cgAV/X6N5eYAVEbLpKT/QJTuKTHhndYDHADLPPM2pe0X
// SIG // BogfjnMMpwIDAQABo4IBqjCCAaYwDgYDVR0PAQH/BAQD
// SIG // AgeAMB8GA1UdJQQYMBYGCisGAQQBgjdMEQEGCCsGAQUF
// SIG // BwMDMB0GA1UdDgQWBBQQBjHV6tDXOT4+/NSMkbW//6Co
// SIG // 5jBUBgNVHREETTBLpEkwRzEtMCsGA1UECxMkTWljcm9z
// SIG // b2Z0IElyZWxhbmQgT3BlcmF0aW9ucyBMaW1pdGVkMRYw
// SIG // FAYDVQQFEw0yMzE1MjIrNTA3NTQxMB8GA1UdIwQYMBaA
// SIG // FH9ZP1Qh2q1P7wXl5qPXLQaUEggxMGAGA1UdHwRZMFcw
// SIG // VaBToFGGT2h0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9w
// SIG // a2lvcHMvY3JsL01pY3Jvc29mdCUyMENvZGUlMjBTaWdu
// SIG // aW5nJTIwUENBJTIwMjAyNC5jcmwwbQYIKwYBBQUHAQEE
// SIG // YTBfMF0GCCsGAQUFBzAChlFodHRwOi8vd3d3Lm1pY3Jv
// SIG // c29mdC5jb20vcGtpb3BzL2NlcnRzL01pY3Jvc29mdCUy
// SIG // MENvZGUlMjBTaWduaW5nJTIwUENBJTIwMjAyNC5jcnQw
// SIG // DAYDVR0TAQH/BAIwADANBgkqhkiG9w0BAQsFAAOCAgEA
// SIG // y174mRjWUCxBQDnYClZpU26m2coMTq0BN1Y+gUFRlfp9
// SIG // H3kGXx1tALbQUmpB9hx4YfjoBoJ6BhQou8UevkCjSRkY
// SIG // QTxRzycyJ65aNkvK7I0bmHj36kIlkUuc6OzpbYUqTYrQ
// SIG // oB7IeltYP9dsKgzYR838mnynQg+n1UMfp0cFlNBc7T5D
// SIG // Km2bTL+SIVzjOWKdgv3VZvXDXVgtgLLmoFnlj0/Nkz/s
// SIG // xqiQEMxI8M+FsIGgRy/UAPgJAlZ5PCrcFf7jkQMU4roy
// SIG // jZH8eoiiLCUc/Z17Ml+huLGOthtJm+VzwY/2UiR1xRic
// SIG // eAh6htMkjujyBZ+N1VWwYe8y9fqu9huswNtvw+W7pJ9F
// SIG // 7ZFT3BQvszCPMqIMF+mNYI9jI2S5uIHeCNSykgPmJT1C
// SIG // MYXmJxt/CNgKho8zcCfJPdhc0CYSHZanQVdIikSR8ACN
// SIG // 4dSj84XThqNJgmMy3XTLBEJNnnU7FzoaRXeI6BXKYTOU
// SIG // 3HrTEhbXzJABMwp6HiRCIS7JX+7nRkW4JRW+RcXtbp7V
// SIG // aexrehTgfm6BBdM4d/uQJJ8B0TR5GSvemvi9XOSH70d0
// SIG // J7IYyIJ6/xPB6Lhe0CZMcPa4NsT+FgW8ek+vdbzYHHua
// SIG // HaIb5wpe8WweS4uO3jDmEmDm7jGcWaOgwPqxL0XoYeTF
// SIG // beFXTcAS432qwkF6xEpDwk4wgga9MIIEpaADAgECAhMz
// SIG // AAAAOTu2Nxm/Bh1nAAAAAAA5MA0GCSqGSIb3DQEBDAUA
// SIG // MIGIMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGlu
// SIG // Z3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMV
// SIG // TWljcm9zb2Z0IENvcnBvcmF0aW9uMTIwMAYDVQQDEylN
// SIG // aWNyb3NvZnQgUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3Jp
// SIG // dHkgMjAxMTAeFw0yNDA4MDgyMDU0MThaFw0zNjAzMjIy
// SIG // MjEzMDRaMFcxCzAJBgNVBAYTAlVTMR4wHAYDVQQKExVN
// SIG // aWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNVBAMTH01p
// SIG // Y3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMjQwggIi
// SIG // MA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDYAZwe
// SIG // 4zjHqpUWBzWtuub+CGPXx/EyoXph3zyDXtYKS2ld3YYN
// SIG // 9uFsB9Oi3B26Z7AbpAgzYra8qNHbUvxFuiP8hC/2y0mP
// SIG // ISqW30LlrrAT6/ams2HA8Qlv6p42+SbCNbPGzToN21QE
// SIG // 70FS+LXH9N2k8nLM/EHgnTNJf8h0TmyfUKmszNa+lTxD
// SIG // ieyy/rhBG+98OkArobPPWtbr9c3qzmDJ7J3kUcAm6clt
// SIG // dSHIIFNHESgw6taY1ScyGyBevqIl120XjrIHiPM7tRck
// SIG // HytH1ZGsmvEplR0P7Tn9t5meFvZNEYttkFvad1IEguTl
// SIG // A5LSscXAphi+rVy3zhklhyCFeGK0yU0+jzbcuURKIxyb
// SIG // mRwK5BfVZx0xEVqE4wM3yN5D/uW+GpVHYYAGe7bTrtW1
// SIG // Z13x2qj2Jdqz7NtI4tNyzlVrIf62nYBNe3rOYS/repVd
// SIG // HlR61YbLLETlibs9jFzAre4sO5RTxvS1yho7JqJ59oKL
// SIG // RnRyLhIOSZyTCVZosXeS0ZZJoGEWSs4cUgsMqBiKtD4W
// SIG // gO2PlT3LeaQh5Io3CCA5tJ5ZCvtCsnqaJXKhptE/xmEE
// SIG // TIRyZRjjplUKKd+sFFVGJJVMvvrw1nhIBKOLO4cTepiG
// SIG // 39jEiEP4iHzGYCcQuvaLpDFFwqzgt0pBP8SJIKX5dtjD
// SIG // NYrZGd+ZzV5DKJVNZQIDAQABo4IBTjCCAUowDgYDVR0P
// SIG // AQH/BAQDAgGGMBAGCSsGAQQBgjcVAQQDAgEAMB0GA1Ud
// SIG // DgQWBBR/WT9UIdqtT+8F5eaj1y0GlBIIMTAZBgkrBgEE
// SIG // AYI3FAIEDB4KAFMAdQBiAEMAQTAPBgNVHRMBAf8EBTAD
// SIG // AQH/MB8GA1UdIwQYMBaAFHItOgIxkEO5FAVO4eqnxzHR
// SIG // I4k0MFoGA1UdHwRTMFEwT6BNoEuGSWh0dHA6Ly9jcmwu
// SIG // bWljcm9zb2Z0LmNvbS9wa2kvY3JsL3Byb2R1Y3RzL01p
// SIG // Y1Jvb0NlckF1dDIwMTFfMjAxMV8wM18yMi5jcmwwXgYI
// SIG // KwYBBQUHAQEEUjBQME4GCCsGAQUFBzAChkJodHRwOi8v
// SIG // d3d3Lm1pY3Jvc29mdC5jb20vcGtpL2NlcnRzL01pY1Jv
// SIG // b0NlckF1dDIwMTFfMjAxMV8wM18yMi5jcnQwDQYJKoZI
// SIG // hvcNAQEMBQADggIBABSUHzgoT+6J5+nyyDCq0pTdVmCs
// SIG // AxYAHXcpjlDtxazPHewf1v4kOg8V7A5+w+VuMDMGHi8r
// SIG // LXBKn5I8+DVEUYGs8jLuckc0IeC6owOLUrU3CYdaKRMa
// SIG // O55+T7jwWJ27tPkx0rlR03tFU0z1YYpcv6Yhaw6N2sUP
// SIG // T+AvjpecnrftoE33pCAkucUvnGH0iL4J9CZLFQVTGFSO
// SIG // UBbv6oZy4bBBRFMxvH779IY4JDvpZKVfbcuhpDeL3Z3e
// SIG // 8mukOmkfct+GojNapsWsQYujlJ8jZen5Lrp/3YkxZ2Ay
// SIG // 06aTpK/5oOVknwog1TDQsbY+MDyguTph5tQ0CLfzDaJG
// SIG // 2x91BrBT9UG87C6HLkqiwrx9PSKN3wz05rHEfWO+RuKl
// SIG // +0U1/AHQT6NCOjhKI39/c7hWbdKjh5uuWFkBOvXGTNrn
// SIG // hNTAdOXTTYByvYExO8yryv34PAdqo1vPDE/1heVebr2R
// SIG // ramvRUi9kWswKwPqwz7n+iRmM+B6YDGRweEurM1kimAb
// SIG // 9FYrAs38YHlPnarl1vW3dGrmJTgefAz3DmCnXN0nveIP
// SIG // sS+KXBIWweeCToAJMGE7v/XS3h9qQ6niWQAAVQ1kUAml
// SIG // 3zuS4MisCgi2F6YoK2WAo1EgXK/lXvDxVjIVU0JdL+Kv
// SIG // CfwFJkDeVuJ9dNXGNi+AOxk0BtYd9hxwL30BElj9MYIZ
// SIG // +zCCGfcCAQEwbjBXMQswCQYDVQQGEwJVUzEeMBwGA1UE
// SIG // ChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSgwJgYDVQQD
// SIG // Ex9NaWNyb3NvZnQgQ29kZSBTaWduaW5nIFBDQSAyMDI0
// SIG // AhMzAAAB/eT3WTHDZNzhAAAAAAH9MA0GCWCGSAFlAwQC
// SIG // AQUAoIGuMBkGCSqGSIb3DQEJAzEMBgorBgEEAYI3AgEE
// SIG // MBwGCisGAQQBgjcCAQsxDjAMBgorBgEEAYI3AgEVMC8G
// SIG // CSqGSIb3DQEJBDEiBCA2uWfYsEn+Xqg6P//C2jtJIrew
// SIG // z8Q0sF/iUjrUTPxzSzBCBgorBgEEAYI3AgEMMTQwMqAU
// SIG // gBIATQBpAGMAcgBvAHMAbwBmAHShGoAYaHR0cDovL3d3
// SIG // dy5taWNyb3NvZnQuY29tMA0GCSqGSIb3DQEBAQUABIIB
// SIG // AB5prmxcqGJGtxHThQk+YgzFf+LuPlaFRpV4MtpSDw5n
// SIG // rLAIedVBD5uizY9SyThaAxwucmOuv0XAelSz7PfL+3sN
// SIG // AZjZoI8EBqSpyddIx1wmKZHEtIByfP1FbHhG0F5lBa2f
// SIG // +WGZOaUf6R3L7KuQ9rBeKCsvdYfeK/8KCovLU/Y7pn2r
// SIG // XvBy+7MA/9OqvP1CVg3Ontz+gz+uuDCNOi6x/2GhO1bB
// SIG // pLQtHcZr0YCQEFXV8KfjjkC2MuYixXogwEusCwcJdf3j
// SIG // SeSQ2rR+tMVcm7IPCB9P1SPofPi/4dKfQ+N2yAEFPcqJ
// SIG // qIv4b0SoJ9ilQ557H5gKBTnJKav9nzcCXCqhghetMIIX
// SIG // qQYKKwYBBAGCNwMDATGCF5kwgheVBgkqhkiG9w0BBwKg
// SIG // gheGMIIXggIBAzEPMA0GCWCGSAFlAwQCAQUAMIIBWgYL
// SIG // KoZIhvcNAQkQAQSgggFJBIIBRTCCAUECAQEGCisGAQQB
// SIG // hFkKAwEwMTANBglghkgBZQMEAgEFAAQgi1BAOEwFbB1s
// SIG // przaU02Vrc2yJPwuyiwQsEwU7VAtvq8CBmoRBXmhRRgT
// SIG // MjAyNjA1MjkwMDQyNDEuMDE4WjAEgAIB9KCB2aSB1jCB
// SIG // 0zELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0
// SIG // b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1p
// SIG // Y3Jvc29mdCBDb3Jwb3JhdGlvbjEtMCsGA1UECxMkTWlj
// SIG // cm9zb2Z0IElyZWxhbmQgT3BlcmF0aW9ucyBMaW1pdGVk
// SIG // MScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046NDMxQS0w
// SIG // NUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1l
// SIG // LVN0YW1wIFNlcnZpY2WgghH7MIIHKDCCBRCgAwIBAgIT
// SIG // MwAAAh1LwJKHOIV+OQABAAACHTANBgkqhkiG9w0BAQsF
// SIG // ADB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGlu
// SIG // Z3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMV
// SIG // TWljcm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1N
// SIG // aWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDAeFw0y
// SIG // NTA4MTQxODQ4MzNaFw0yNjExMTMxODQ4MzNaMIHTMQsw
// SIG // CQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQ
// SIG // MA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
// SIG // b2Z0IENvcnBvcmF0aW9uMS0wKwYDVQQLEyRNaWNyb3Nv
// SIG // ZnQgSXJlbGFuZCBPcGVyYXRpb25zIExpbWl0ZWQxJzAl
// SIG // BgNVBAsTHm5TaGllbGQgVFNTIEVTTjo0MzFBLTA1RTAt
// SIG // RDk0NzElMCMGA1UEAxMcTWljcm9zb2Z0IFRpbWUtU3Rh
// SIG // bXAgU2VydmljZTCCAiIwDQYJKoZIhvcNAQEBBQADggIP
// SIG // ADCCAgoCggIBAKK0oGgAPKDpeKYee+M8NvXoFDfAw3qU
// SIG // Ry1/BTNcxzSZlxuiq0qlCsM3Cmn6KbmHT0xE0wr2/WiX
// SIG // xErgFNIhjVBSPw+kdJL3X6XtqD1/hN7G00LxouCTx+an
// SIG // SGFGieOVf+G6nvHjb21s6QvmSox9fdw3oiNVwCPdfCaE
// SIG // JgYZRF6P06J9e9tZbmSYIp3LH+S4zGN41/OFsl1El93b
// SIG // Eu4f+8VSPsNco4O6WvtMt6P5ntk7L+lCVHUk0GqeTkRk
// SIG // nwp3JZz9c9yIoliFq91aO2iD1rICc6t5uRsacVBwkJPK
// SIG // s1IZOdMv7gfixhN1iCtgu+4svYhbEn0i1J8jBMxkQ1vZ
// SIG // lx0+Dx+zs8+gh6kBIjb8HB6pb5QodaR0IdTV0EgKjqFQ
// SIG // bOZounmrH+ssVk33uQ60e/edN6/KVOlagtmPVzEVOMB/
// SIG // UG2F2LCFGd9yZp3cttltSwQwG8QT0BwgZZ3Bg1NwYHYV
// SIG // VFS3vNJoIBTvfBXZFoaOu8OJD3Qk0ZL3b5GPD60GBP50
// SIG // Ix1wmtIOy3DLbWW+nozB30PrVFl7+vp2eGJ5K9jpGsXJ
// SIG // RQsOESGDTFg9ugFm0I/1hHc4GtfHyrcOui+YM1z82uox
// SIG // QXzyXihNx/EALsKYq5h+JrPuZ1IzTUDpjYKiZ9FNft2J
// SIG // +wpbMA+/WDdK933W2ATAwKQWSaTZSu6ux10bAgMBAAGj
// SIG // ggFJMIIBRTAdBgNVHQ4EFgQUhFnwcTRGpmbV5vIJfdmK
// SIG // vNI38V0wHwYDVR0jBBgwFoAUn6cVXQBeYl2D9OXSZacb
// SIG // UzUZ6XIwXwYDVR0fBFgwVjBUoFKgUIZOaHR0cDovL3d3
// SIG // dy5taWNyb3NvZnQuY29tL3BraW9wcy9jcmwvTWljcm9z
// SIG // b2Z0JTIwVGltZS1TdGFtcCUyMFBDQSUyMDIwMTAoMSku
// SIG // Y3JsMGwGCCsGAQUFBwEBBGAwXjBcBggrBgEFBQcwAoZQ
// SIG // aHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9j
// SIG // ZXJ0cy9NaWNyb3NvZnQlMjBUaW1lLVN0YW1wJTIwUENB
// SIG // JTIwMjAxMCgxKS5jcnQwDAYDVR0TAQH/BAIwADAWBgNV
// SIG // HSUBAf8EDDAKBggrBgEFBQcDCDAOBgNVHQ8BAf8EBAMC
// SIG // B4AwDQYJKoZIhvcNAQELBQADggIBAJHcHgeMsby7KSyq
// SIG // tA/posg+ENBHMVRaTWbicYkeeIFkZHkww7spjXgdNyYZ
// SIG // bAaW8EmCebmUoAwQr8BxA9lS/JSaRZTqayc8bF1gtjU3
// SIG // wPjvjzuRZOY8Oix4eo3gQAwxHUAMdx6ou2ZtCcL0Pd8+
// SIG // X+nbcZJtvVqjnB2F0V3wEMMtYUqy18n3m5akeuo6T//Z
// SIG // 9HwpFlOIILFI0KUNjYI9Q1dPSeGN8u6fTXfNfl7OqmKP
// SIG // vu0SpvKogf+TQ3ooDi45QHhYIhFyEVCVvpicqqUMPjjk
// SIG // ZWqnBY0fB7tBvv+2zHXpOvGF/pD6QwZO1HviP8YImCdc
// SIG // XA0QZ/73My7Te9vkSJQ+FIF2C7gUgpP/6QxD1+c9/Qq/
// SIG // q5HOhOGNvBT5OAYZaAMr6etvD+MXxJUGPE3Ma2lG2Uoc
// SIG // qaHBOp8veQ9StQZJbWZqx1SgsZoJZ7jpTNeTSiK1xZVw
// SIG // s3aqQrSMEONe8DQFRf0Az78827pj3U4un29LS20nGKG1
// SIG // es72wbDLChDBOE49W/aCFwvHcmyauJ226BF2KUcItUAG
// SIG // 6Uja5/j8Rlvbn9autxZzCbuIJtzoet541v4lX+9t6rs8
// SIG // h60oo1jIGNB4kYh0ItCcrtIfDHYUVKe5sW5i0HJD4jhc
// SIG // AJSGlDf5O9ucv2i1qZEVOn6pi5RDsh+Vqci3dtwGMva/
// SIG // L/kKG2urMIIHcTCCBVmgAwIBAgITMwAAABXF52ueAptJ
// SIG // mQAAAAAAFTANBgkqhkiG9w0BAQsFADCBiDELMAkGA1UE
// SIG // BhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNV
// SIG // BAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBD
// SIG // b3Jwb3JhdGlvbjEyMDAGA1UEAxMpTWljcm9zb2Z0IFJv
// SIG // b3QgQ2VydGlmaWNhdGUgQXV0aG9yaXR5IDIwMTAwHhcN
// SIG // MjEwOTMwMTgyMjI1WhcNMzAwOTMwMTgzMjI1WjB8MQsw
// SIG // CQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQ
// SIG // MA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9z
// SIG // b2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3Nv
// SIG // ZnQgVGltZS1TdGFtcCBQQ0EgMjAxMDCCAiIwDQYJKoZI
// SIG // hvcNAQEBBQADggIPADCCAgoCggIBAOThpkzntHIhC3mi
// SIG // y9ckeb0O1YLT/e6cBwfSqWxOdcjKNVf2AX9sSuDivbk+
// SIG // F2Az/1xPx2b3lVNxWuJ+Slr+uDZnhUYjDLWNE893MsAQ
// SIG // GOhgfWpSg0S3po5GawcU88V29YZQ3MFEyHFcUTE3oAo4
// SIG // bo3t1w/YJlN8OWECesSq/XJprx2rrPY2vjUmZNqYO7oa
// SIG // ezOtgFt+jBAcnVL+tuhiJdxqD89d9P6OU8/W7IVWTe/d
// SIG // vI2k45GPsjksUZzpcGkNyjYtcI4xyDUoveO0hyTD4MmP
// SIG // frVUj9z6BVWYbWg7mka97aSueik3rMvrg0XnRm7KMtXA
// SIG // hjBcTyziYrLNueKNiOSWrAFKu75xqRdbZ2De+JKRHh09
// SIG // /SDPc31BmkZ1zcRfNN0Sidb9pSB9fvzZnkXftnIv231f
// SIG // gLrbqn427DZM9ituqBJR6L8FA6PRc6ZNN3SUHDSCD/AQ
// SIG // 8rdHGO2n6Jl8P0zbr17C89XYcz1DTsEzOUyOArxCaC4Q
// SIG // 6oRRRuLRvWoYWmEBc8pnol7XKHYC4jMYctenIPDC+hIK
// SIG // 12NvDMk2ZItboKaDIV1fMHSRlJTYuVD5C4lh8zYGNRiE
// SIG // R9vcG9H9stQcxWv2XFJRXRLbJbqvUAV6bMURHXLvjflS
// SIG // xIUXk8A8FdsaN8cIFRg/eKtFtvUeh17aj54WcmnGrnu3
// SIG // tz5q4i6tAgMBAAGjggHdMIIB2TASBgkrBgEEAYI3FQEE
// SIG // BQIDAQABMCMGCSsGAQQBgjcVAgQWBBQqp1L+ZMSavoKR
// SIG // PEY1Kc8Q/y8E7jAdBgNVHQ4EFgQUn6cVXQBeYl2D9OXS
// SIG // ZacbUzUZ6XIwXAYDVR0gBFUwUzBRBgwrBgEEAYI3TIN9
// SIG // AQEwQTA/BggrBgEFBQcCARYzaHR0cDovL3d3dy5taWNy
// SIG // b3NvZnQuY29tL3BraW9wcy9Eb2NzL1JlcG9zaXRvcnku
// SIG // aHRtMBMGA1UdJQQMMAoGCCsGAQUFBwMIMBkGCSsGAQQB
// SIG // gjcUAgQMHgoAUwB1AGIAQwBBMAsGA1UdDwQEAwIBhjAP
// SIG // BgNVHRMBAf8EBTADAQH/MB8GA1UdIwQYMBaAFNX2VsuP
// SIG // 6KJcYmjRPZSQW9fOmhjEMFYGA1UdHwRPME0wS6BJoEeG
// SIG // RWh0dHA6Ly9jcmwubWljcm9zb2Z0LmNvbS9wa2kvY3Js
// SIG // L3Byb2R1Y3RzL01pY1Jvb0NlckF1dF8yMDEwLTA2LTIz
// SIG // LmNybDBaBggrBgEFBQcBAQROMEwwSgYIKwYBBQUHMAKG
// SIG // Pmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9wa2kvY2Vy
// SIG // dHMvTWljUm9vQ2VyQXV0XzIwMTAtMDYtMjMuY3J0MA0G
// SIG // CSqGSIb3DQEBCwUAA4ICAQCdVX38Kq3hLB9nATEkW+Ge
// SIG // ckv8qW/qXBS2Pk5HZHixBpOXPTEztTnXwnE2P9pkbHzQ
// SIG // dTltuw8x5MKP+2zRoZQYIu7pZmc6U03dmLq2HnjYNi6c
// SIG // qYJWAAOwBb6J6Gngugnue99qb74py27YP0h1AdkY3m2C
// SIG // DPVtI1TkeFN1JFe53Z/zjj3G82jfZfakVqr3lbYoVSfQ
// SIG // JL1AoL8ZthISEV09J+BAljis9/kpicO8F7BUhUKz/Aye
// SIG // ixmJ5/ALaoHCgRlCGVJ1ijbCHcNhcy4sa3tuPywJeBTp
// SIG // kbKpW99Jo3QMvOyRgNI95ko+ZjtPu4b6MhrZlvSP9pEB
// SIG // 9s7GdP32THJvEKt1MMU0sHrYUP4KWN1APMdUbZ1jdEgs
// SIG // sU5HLcEUBHG/ZPkkvnNtyo4JvbMBV0lUZNlz138eW0QB
// SIG // jloZkWsNn6Qo3GcZKCS6OEuabvshVGtqRRFHqfG3rsjo
// SIG // iV5PndLQTHa1V1QJsWkBRH58oWFsc/4Ku+xBZj1p/cvB
// SIG // QUl+fpO+y/g75LcVv7TOPqUxUYS8vwLBgqJ7Fx0ViY1w
// SIG // /ue10CgaiQuPNtq6TPmb/wrpNPgkNWcr4A245oyZ1uEi
// SIG // 6vAnQj0llOZ0dFtq0Z4+7X6gMTN9vMvpe784cETRkPHI
// SIG // qzqKOghif9lwY1NNje6CbaUFEMFxBmoQtB1VM1izoXBm
// SIG // 8qGCA1YwggI+AgEBMIIBAaGB2aSB1jCB0zELMAkGA1UE
// SIG // BhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNV
// SIG // BAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBD
// SIG // b3Jwb3JhdGlvbjEtMCsGA1UECxMkTWljcm9zb2Z0IEly
// SIG // ZWxhbmQgT3BlcmF0aW9ucyBMaW1pdGVkMScwJQYDVQQL
// SIG // Ex5uU2hpZWxkIFRTUyBFU046NDMxQS0wNUUwLUQ5NDcx
// SIG // JTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNl
// SIG // cnZpY2WiIwoBATAHBgUrDgMCGgMVALqDvgSm3186sn4v
// SIG // RixHVh5Ai3k/oIGDMIGApH4wfDELMAkGA1UEBhMCVVMx
// SIG // EzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1Jl
// SIG // ZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3Jh
// SIG // dGlvbjEmMCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3Rh
// SIG // bXAgUENBIDIwMTAwDQYJKoZIhvcNAQELBQACBQDtwsOd
// SIG // MCIYDzIwMjYwNTI4MTMzNzMzWhgPMjAyNjA1MjkxMzM3
// SIG // MzNaMHQwOgYKKwYBBAGEWQoEATEsMCowCgIFAO3Cw50C
// SIG // AQAwBwIBAAICKOswBwIBAAICEsYwCgIFAO3EFR0CAQAw
// SIG // NgYKKwYBBAGEWQoEAjEoMCYwDAYKKwYBBAGEWQoDAqAK
// SIG // MAgCAQACAwehIKEKMAgCAQACAwGGoDANBgkqhkiG9w0B
// SIG // AQsFAAOCAQEAL5WU5FQNoPyAUm0S8H1VKi17L72aD7Mg
// SIG // y3RZ+YPY5wF+8RZZyKGDi/idvC8rVbbLD4ctHHN1a60i
// SIG // VSTZyz/xmqZr1c3bBwPqb/qprd1+V/AQ+/ok5J/ZR4lg
// SIG // r3DPzIYmwsL6bmsRcUALbO6RQRLZROmz/TLmgmMno4cu
// SIG // EkMU1eAVda5Re3aidg9fqNdaZFJGi4FBKFGgwI7jb+Q8
// SIG // GOnVegQjdM5bncSGdq0ZiZCpEj5h+1Z8kI95F+gzMp00
// SIG // /WqLaR7lehtZsMW7NiW23LcGZZKfzAbFU6nIF94Nxpq2
// SIG // qAenJGPuF/tYGywq+eYEYlRTQPrrYQei97cLi5qp3p5I
// SIG // 0jGCBA0wggQJAgEBMIGTMHwxCzAJBgNVBAYTAlVTMRMw
// SIG // EQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRt
// SIG // b25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRp
// SIG // b24xJjAkBgNVBAMTHU1pY3Jvc29mdCBUaW1lLVN0YW1w
// SIG // IFBDQSAyMDEwAhMzAAACHUvAkoc4hX45AAEAAAIdMA0G
// SIG // CWCGSAFlAwQCAQUAoIIBSjAaBgkqhkiG9w0BCQMxDQYL
// SIG // KoZIhvcNAQkQAQQwLwYJKoZIhvcNAQkEMSIEIOPe9LV/
// SIG // Q9d4Su36ZDHZ5TQPl5BFveheH+nljQouCXYvMIH6Bgsq
// SIG // hkiG9w0BCRACLzGB6jCB5zCB5DCBvQQgsbaVzFxIiyc6
// SIG // 6jO+3qeK0zcKzDo+oKVjfYWb6Y+UBVEwgZgwgYCkfjB8
// SIG // MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3Rv
// SIG // bjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWlj
// SIG // cm9zb2Z0IENvcnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNy
// SIG // b3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAh1L
// SIG // wJKHOIV+OQABAAACHTAiBCBLER24qpY4jjVnBpodXrSr
// SIG // KJut7qtcRYxUUXzhNtPBRzANBgkqhkiG9w0BAQsFAASC
// SIG // AgCbGZCChx86hNQVH1gSkWS8X7HKQDqH9FI79NiUf5Kh
// SIG // 0C/4tteWWXK4bH6xfUZDamZ4EY/X2lVONlH1W7LiZX0o
// SIG // KuyoRAY5CYonyO3uAKAQ+lU8/25X0WPYeD6hdeApWwxO
// SIG // 2GQ7RofYTI4ADBO86Gzy7WjMwavcZdPYDZfjybAbzQje
// SIG // rKNvg+u5hr/sbtL2zmbqQo3/BiIOGEOnYEDkVQz7yk55
// SIG // Ea5eKFBnz/7s9Bpn9v7chB3vvxjaq3FNFhdXAvFGFQFw
// SIG // FPqfAeCSL36Vz7rBiy+/qjM0mOuJ+wxUiSMDsAIMc+xE
// SIG // T3gZH4V/sfQYGBVNr86S1NkwHRTlYiNJkcM10iRRifva
// SIG // pZZMbKoRrR5+26TzCyc371B4Uv+R/Vw6vVEB4BINVICR
// SIG // cAk0TMN+k3UTUip1lzyU2YtJStz3PCCaESk+WjSYMOaL
// SIG // mr7vOFX5ajBKY8fKRmjeCnKhAwRWhz/mwKwWoYu1evAE
// SIG // xNcHCfziZ28G5F0GQYAoLZVhx2l36xPGpivAIqfbmBkI
// SIG // NC9YsNm78chS97ZGGP7Q4PFnAeTY5VWyu9xbfxk5sn/7
// SIG // qbOP1p9koKLNyMz80D2jnXx/zHWh8ygEOLZIOxD2CT7Q
// SIG // TdqdhsZXN0fxqdG8zU5n8zkkBLxJeBIfj8qLa4QZI3Y9
// SIG // AjSIWYif11YhOwIt0GJF42Fs8A==
// SIG // End signature block
