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
/*!
** Unobtrusive validation support library for jQuery and jQuery Validate
** Copyright (C) Microsoft Corporation. All rights reserved.
*/
/*jslint white: true, browser: true, onevar: true, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, regexp: true, newcap: true, immed: true, strict: false */
/*global document: false, jQuery: false */
(function ($) {
var $jQval = $.validator,
adapters,
data_validation = "unobtrusiveValidation";
function setValidationValues(options, ruleName, value) {
options.rules[ruleName] = value;
if (options.message) {
options.messages[ruleName] = options.message;
}
}
function splitAndTrim(value) {
return value.replace(/^\s+|\s+$/g, "").split(/\s*,\s*/g);
}
function escapeAttributeValue(value) {
// As mentioned on http://api.jquery.com/category/selectors/
return value.replace(/([!"#$%&'()*+,./:;<=>?@\[\\\]^`{|}~])/g, "\\$1");
}
function getModelPrefix(fieldName) {
return fieldName.substr(0, fieldName.lastIndexOf(".") + 1);
}
function appendModelPrefix(value, prefix) {
if (value.indexOf("*.") === 0) {
value = value.replace("*.", prefix);
}
return value;
}
function onError(error, inputElement) {  // 'this' is the form element
var container = $(this).find("[data-valmsg-for='" + escapeAttributeValue(inputElement[0].name) + "']"),
replaceAttrValue = container.attr("data-valmsg-replace"),
replace = replaceAttrValue ? $.parseJSON(replaceAttrValue) !== false : null;
container.removeClass("field-validation-valid").addClass("field-validation-error");
error.data("unobtrusiveContainer", container);
if (replace) {
container.empty();
error.removeClass("input-validation-error").appendTo(container);
}
else {
error.hide();
}
}
function onErrors(event, validator) {  // 'this' is the form element
var container = $(this).find("[data-valmsg-summary=true]"),
list = container.find("ul");
if (list && list.length && validator.errorList.length) {
list.empty();
container.addClass("validation-summary-errors").removeClass("validation-summary-valid");
$.each(validator.errorList, function () {
$("<li />").html(this.message).appendTo(list);
});
}
}
function onSuccess(error) {  // 'this' is the form element
var container = error.data("unobtrusiveContainer"),
replaceAttrValue = container.attr("data-valmsg-replace"),
replace = replaceAttrValue ? $.parseJSON(replaceAttrValue) : null;
if (container) {
container.addClass("field-validation-valid").removeClass("field-validation-error");
error.removeData("unobtrusiveContainer");
if (replace) {
container.empty();
}
}
}
function onReset(event) {  // 'this' is the form element
var $form = $(this);
$form.data("validator").resetForm();
$form.find(".validation-summary-errors")
.addClass("validation-summary-valid")
.removeClass("validation-summary-errors");
$form.find(".field-validation-error")
.addClass("field-validation-valid")
.removeClass("field-validation-error")
.removeData("unobtrusiveContainer")
.find(">*")  // If we were using valmsg-replace, get the underlying error
.removeData("unobtrusiveContainer");
}
function validationInfo(form) {
var $form = $(form),
result = $form.data(data_validation),
onResetProxy = $.proxy(onReset, form);
if (!result) {
result = {
options: {  // options structure passed to jQuery Validate's validate() method
errorClass: "input-validation-error",
errorElement: "span",
errorPlacement: $.proxy(onError, form),
invalidHandler: $.proxy(onErrors, form),
messages: {},
rules: {},
success: $.proxy(onSuccess, form)
},
attachValidation: function () {
$form
.unbind("reset." + data_validation, onResetProxy)
.bind("reset." + data_validation, onResetProxy)
.validate(this.options);
},
validate: function () {  // a validation function that is called by unobtrusive Ajax
$form.validate();
return $form.valid();
}
};
$form.data(data_validation, result);
}
return result;
}
$jQval.unobtrusive = {
adapters: [],
parseElement: function (element, skipAttach) {
/// <summary>
/// Parses a single HTML element for unobtrusive validation attributes.
/// </summary>
/// <param name="element" domElement="true">The HTML element to be parsed.</param>
/// <param name="skipAttach" type="Boolean">[Optional] true to skip attaching the
/// validation to the form. If parsing just this single element, you should specify true.
/// If parsing several elements, you should specify false, and manually attach the validation
/// to the form when you are finished. The default is false.</param>
var $element = $(element),
form = $element.parents("form")[0],
valInfo, rules, messages;
if (!form) {  // Cannot do client-side validation without a form
return;
}
valInfo = validationInfo(form);
valInfo.options.rules[element.name] = rules = {};
valInfo.options.messages[element.name] = messages = {};
$.each(this.adapters, function () {
var prefix = "data-val-" + this.name,
message = $element.attr(prefix),
paramValues = {};
if (message !== undefined) {  // Compare against undefined, because an empty message is legal (and falsy)
prefix += "-";
$.each(this.params, function () {
paramValues[this] = $element.attr(prefix + this);
});
this.adapt({
element: element,
form: form,
message: message,
params: paramValues,
rules: rules,
messages: messages
});
}
});
$.extend(rules, { "__dummy__": true });
if (!skipAttach) {
valInfo.attachValidation();
}
},
parse: function (selector) {
/// <summary>
/// Parses all the HTML elements in the specified selector. It looks for input elements decorated
/// with the [data-val=true] attribute value and enables validation according to the data-val-*
/// attribute values.
/// </summary>
/// <param name="selector" type="String">Any valid jQuery selector.</param>
var $forms = $(selector)
.parents("form")
.andSelf()
.add($(selector).find("form"))
.filter("form");
// :input is a psuedoselector provided by jQuery which selects input and input-like elements
// combining :input with other selectors significantly decreases performance.
$(selector).find(":input").filter("[data-val=true]").each(function () {
$jQval.unobtrusive.parseElement(this, true);
});
$forms.each(function () {
var info = validationInfo(this);
if (info) {
info.attachValidation();
}
});
}
};
adapters = $jQval.unobtrusive.adapters;
adapters.add = function (adapterName, params, fn) {
/// <summary>Adds a new adapter to convert unobtrusive HTML into a jQuery Validate validation.</summary>
/// <param name="adapterName" type="String">The name of the adapter to be added. This matches the name used
/// in the data-val-nnnn HTML attribute (where nnnn is the adapter name).</param>
/// <param name="params" type="Array" optional="true">[Optional] An array of parameter names (strings) that will
/// be extracted from the data-val-nnnn-mmmm HTML attributes (where nnnn is the adapter name, and
/// mmmm is the parameter name).</param>
/// <param name="fn" type="Function">The function to call, which adapts the values from the HTML
/// attributes into jQuery Validate rules and/or messages.</param>
/// <returns type="jQuery.validator.unobtrusive.adapters" />
if (!fn) {  // Called with no params, just a function
fn = params;
params = [];
}
this.push({ name: adapterName, params: params, adapt: fn });
return this;
};
adapters.addBool = function (adapterName, ruleName) {
/// <summary>Adds a new adapter to convert unobtrusive HTML into a jQuery Validate validation, where
/// the jQuery Validate validation rule has no parameter values.</summary>
/// <param name="adapterName" type="String">The name of the adapter to be added. This matches the name used
/// in the data-val-nnnn HTML attribute (where nnnn is the adapter name).</param>
/// <param name="ruleName" type="String" optional="true">[Optional] The name of the jQuery Validate rule. If not provided, the value
/// of adapterName will be used instead.</param>
/// <returns type="jQuery.validator.unobtrusive.adapters" />
return this.add(adapterName, function (options) {
setValidationValues(options, ruleName || adapterName, true);
});
};
adapters.addMinMax = function (adapterName, minRuleName, maxRuleName, minMaxRuleName, minAttribute, maxAttribute) {
/// <summary>Adds a new adapter to convert unobtrusive HTML into a jQuery Validate validation, where
/// the jQuery Validate validation has three potential rules (one for min-only, one for max-only, and
/// one for min-and-max). The HTML parameters are expected to be named -min and -max.</summary>
/// <param name="adapterName" type="String">The name of the adapter to be added. This matches the name used
/// in the data-val-nnnn HTML attribute (where nnnn is the adapter name).</param>
/// <param name="minRuleName" type="String">The name of the jQuery Validate rule to be used when you only
/// have a minimum value.</param>
/// <param name="maxRuleName" type="String">The name of the jQuery Validate rule to be used when you only
/// have a maximum value.</param>
/// <param name="minMaxRuleName" type="String">The name of the jQuery Validate rule to be used when you
/// have both a minimum and maximum value.</param>
/// <param name="minAttribute" type="String" optional="true">[Optional] The name of the HTML attribute that
/// contains the minimum value. The default is "min".</param>
/// <param name="maxAttribute" type="String" optional="true">[Optional] The name of the HTML attribute that
/// contains the maximum value. The default is "max".</param>
/// <returns type="jQuery.validator.unobtrusive.adapters" />
return this.add(adapterName, [minAttribute || "min", maxAttribute || "max"], function (options) {
var min = options.params.min,
max = options.params.max;
if (min && max) {
setValidationValues(options, minMaxRuleName, [min, max]);
}
else if (min) {
setValidationValues(options, minRuleName, min);
}
else if (max) {
setValidationValues(options, maxRuleName, max);
}
});
};
adapters.addSingleVal = function (adapterName, attribute, ruleName) {
/// <summary>Adds a new adapter to convert unobtrusive HTML into a jQuery Validate validation, where
/// the jQuery Validate validation rule has a single value.</summary>
/// <param name="adapterName" type="String">The name of the adapter to be added. This matches the name used
/// in the data-val-nnnn HTML attribute(where nnnn is the adapter name).</param>
/// <param name="attribute" type="String">[Optional] The name of the HTML attribute that contains the value.
/// The default is "val".</param>
/// <param name="ruleName" type="String" optional="true">[Optional] The name of the jQuery Validate rule. If not provided, the value
/// of adapterName will be used instead.</param>
/// <returns type="jQuery.validator.unobtrusive.adapters" />
return this.add(adapterName, [attribute || "val"], function (options) {
setValidationValues(options, ruleName || adapterName, options.params[attribute]);
});
};
$jQval.addMethod("__dummy__", function (value, element, params) {
return true;
});
$jQval.addMethod("regex", function (value, element, params) {
var match;
if (this.optional(element)) {
return true;
}
match = new RegExp(params).exec(value);
return (match && (match.index === 0) && (match[0].length === value.length));
});
$jQval.addMethod("nonalphamin", function (value, element, nonalphamin) {
var match;
if (nonalphamin) {
match = value.match(/\W/g);
match = match && match.length >= nonalphamin;
}
return match;
});
if ($jQval.methods.extension) {
adapters.addSingleVal("accept", "mimtype");
adapters.addSingleVal("extension", "extension");
} else {
// for backward compatibility, when the 'extension' validation method does not exist, such as with versions
// of JQuery Validation plugin prior to 1.10, we should use the 'accept' method for
// validating the extension, and ignore mime-type validations as they are not supported.
adapters.addSingleVal("extension", "extension", "accept");
}
adapters.addSingleVal("regex", "pattern");
adapters.addBool("creditcard").addBool("date").addBool("digits").addBool("email").addBool("number").addBool("url");
adapters.addMinMax("length", "minlength", "maxlength", "rangelength").addMinMax("range", "min", "max", "range");
adapters.add("equalto", ["other"], function (options) {
var prefix = getModelPrefix(options.element.name),
other = options.params.other,
fullOtherName = appendModelPrefix(other, prefix),
element = $(options.form).find(":input").filter("[name='" + escapeAttributeValue(fullOtherName) + "']")[0];
setValidationValues(options, "equalTo", element);
});
adapters.add("required", function (options) {
// jQuery Validate equates "required" with "mandatory" for checkbox elements
if (options.element.tagName.toUpperCase() !== "INPUT" || options.element.type.toUpperCase() !== "CHECKBOX") {
setValidationValues(options, "required", true);
}
});
adapters.add("remote", ["url", "type", "additionalfields"], function (options) {
var value = {
url: options.params.url,
type: options.params.type || "GET",
data: {}
},
prefix = getModelPrefix(options.element.name);
$.each(splitAndTrim(options.params.additionalfields || options.element.name), function (i, fieldName) {
var paramName = appendModelPrefix(fieldName, prefix);
value.data[paramName] = function () {
return $(options.form).find(":input").filter("[name='" + escapeAttributeValue(paramName) + "']").val();
};
});
setValidationValues(options, "remote", value);
});
adapters.add("password", ["min", "nonalphamin", "regex"], function (options) {
if (options.params.min) {
setValidationValues(options, "minlength", options.params.min);
}
if (options.params.nonalphamin) {
setValidationValues(options, "nonalphamin", options.params.nonalphamin);
}
if (options.params.regex) {
setValidationValues(options, "regex", options.params.regex);
}
});
$(function () {
$jQval.unobtrusive.parse(document);
});
}(jQuery));

// SIG // Begin signature block
// SIG // MIInXAYJKoZIhvcNAQcCoIInTTCCJ0kCAQExDzANBglg
// SIG // hkgBZQMEAgEFADB3BgorBgEEAYI3AgEEoGkwZzAyBgor
// SIG // BgEEAYI3AgEeMCQCAQEEEBDgyQbOONQRoqMAEEvTUJAC
// SIG // AQACAQACAQACAQACAQAwMTANBglghkgBZQMEAgEFAAQg
// SIG // uN+x7CLKtUQrxuaCz7jFZvt+a6IMdI7wV86RPq+66E6g
// SIG // ggzPMIIGCjCCA/KgAwIBAgITMwAAAf7+iki1zsRg8QAA
// SIG // AAAB/jANBgkqhkiG9w0BAQsFADBXMQswCQYDVQQGEwJV
// SIG // UzEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9u
// SIG // MSgwJgYDVQQDEx9NaWNyb3NvZnQgQ29kZSBTaWduaW5n
// SIG // IFBDQSAyMDI0MB4XDTI2MDQxNjE4NTg1MloXDTI3MDQx
// SIG // NTE4NTg1MlowgYgxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
// SIG // EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4w
// SIG // HAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xMjAw
// SIG // BgNVBAMTKU1pY3Jvc29mdCAzcmQgUGFydHkgQXBwbGlj
// SIG // YXRpb24gQ29tcG9uZW50MIIBIjANBgkqhkiG9w0BAQEF
// SIG // AAOCAQ8AMIIBCgKCAQEAv1RjgRSjfl8SE93CFRZLi4N7
// SIG // hmn0IkvQqsfJc1+80zFVHlZnA2HGF7IpvPeqinp4SBpe
// SIG // dfM69fqNJ+id+q8ZhHP6OsW2//iI3bQED00ekouNByvJ
// SIG // H2QcqJATkcgsxjOPVYj4SOqcfR16iGU3KMpNZvydzu/Z
// SIG // eOxbpZnfl0mcLmeqDdjexv5f0w8dieu9Jh26TIL1zv7o
// SIG // Sd0St8Y1eZFQCZeIce5m6jGgRdho0LoIHtdLfR3a9giZ
// SIG // KYzuHiLmOh3W6uu7kwf24wiRsdRtU0yp2QsjaWGgrdpX
// SIG // VRMwyzaKvi4OMNJENmSFzOCZcGMBQHen5QRXas4T2mx3
// SIG // EmZEByYdYQIDAQABo4IBmzCCAZcwDgYDVR0PAQH/BAQD
// SIG // AgeAMB8GA1UdJQQYMBYGCisGAQQBgjdMEQEGCCsGAQUF
// SIG // BwMDMB0GA1UdDgQWBBQmGTbv1kPrIUXGSzs97yJZtFaq
// SIG // FTBFBgNVHREEPjA8pDowODEeMBwGA1UECxMVTWljcm9z
// SIG // b2Z0IENvcnBvcmF0aW9uMRYwFAYDVQQFEw0yMzE1MjIr
// SIG // NTA3NTMxMB8GA1UdIwQYMBaAFH9ZP1Qh2q1P7wXl5qPX
// SIG // LQaUEggxMGAGA1UdHwRZMFcwVaBToFGGT2h0dHA6Ly93
// SIG // d3cubWljcm9zb2Z0LmNvbS9wa2lvcHMvY3JsL01pY3Jv
// SIG // c29mdCUyMENvZGUlMjBTaWduaW5nJTIwUENBJTIwMjAy
// SIG // NC5jcmwwbQYIKwYBBQUHAQEEYTBfMF0GCCsGAQUFBzAC
// SIG // hlFodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3Bz
// SIG // L2NlcnRzL01pY3Jvc29mdCUyMENvZGUlMjBTaWduaW5n
// SIG // JTIwUENBJTIwMjAyNC5jcnQwDAYDVR0TAQH/BAIwADAN
// SIG // BgkqhkiG9w0BAQsFAAOCAgEAHOf/iJrPCpgPWpNTX6BF
// SIG // WYi9rR5/fn97/d+ZHac+/R/2bPc++JzQ4EfFVt6bM0Zb
// SIG // 4EphOAzJQI9B+yltQST/qG0oVMpAUIs8vJgBRbimu/r0
// SIG // OMhZZbRkWfYsKK31vac0B3PSRhkj/0pN/8gApEuATBsp
// SIG // NT6VPZB0SfQ4rg/U/sohdvtoRIYqrP1P+kBwWeQUthaM
// SIG // oOVl5nI8upWghZZMeCj6kx4OeXAPp6zzYlK5mEnoCW4J
// SIG // awcxoaqhFhtJTVaEWWDK5vkjGeBbNbvwkK4e3/16gGW+
// SIG // 8WklZtzg10KPhqX0jRV0bG4IiItEPUqUQyRj2aN2EACH
// SIG // FJeJBstrSc5BSp9vnmRcvdnrnnwGf2NSPiR1193Lx/0W
// SIG // LhlJkscqM7Qv2Dsu6feXS5xLLIPRUEKPCA0Y5xJq1+f7
// SIG // JXB1WxQxAxVKZq6tT1X28pe99xIGiyQYtiP1PSy0TqMJ
// SIG // ePWicHUEIYtWn9KifSvZKA/LrlKCqiG2Yg5zSeZ+Ezvi
// SIG // Q3bLHQy43Mog2KtfArR4R+ZertkNoDe7w9LNUjwPvV2H
// SIG // kYFY4FjXNFZBLLaDdECMu79XQVoC5ANGzb7VnTM1plM5
// SIG // rN1+suCJ8ygMo7rUa1/Vi2zRlYuyfZB7WnAZUknCAUI1
// SIG // kFEJexnmZXQYBV+dokvoirtl6k4/Uu5NDOuryxqYFZFc
// SIG // Nyswgga9MIIEpaADAgECAhMzAAAAOTu2Nxm/Bh1nAAAA
// SIG // AAA5MA0GCSqGSIb3DQEBDAUAMIGIMQswCQYDVQQGEwJV
// SIG // UzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMH
// SIG // UmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBv
// SIG // cmF0aW9uMTIwMAYDVQQDEylNaWNyb3NvZnQgUm9vdCBD
// SIG // ZXJ0aWZpY2F0ZSBBdXRob3JpdHkgMjAxMTAeFw0yNDA4
// SIG // MDgyMDU0MThaFw0zNjAzMjIyMjEzMDRaMFcxCzAJBgNV
// SIG // BAYTAlVTMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9y
// SIG // YXRpb24xKDAmBgNVBAMTH01pY3Jvc29mdCBDb2RlIFNp
// SIG // Z25pbmcgUENBIDIwMjQwggIiMA0GCSqGSIb3DQEBAQUA
// SIG // A4ICDwAwggIKAoICAQDYAZwe4zjHqpUWBzWtuub+CGPX
// SIG // x/EyoXph3zyDXtYKS2ld3YYN9uFsB9Oi3B26Z7AbpAgz
// SIG // Yra8qNHbUvxFuiP8hC/2y0mPISqW30LlrrAT6/ams2HA
// SIG // 8Qlv6p42+SbCNbPGzToN21QE70FS+LXH9N2k8nLM/EHg
// SIG // nTNJf8h0TmyfUKmszNa+lTxDieyy/rhBG+98OkArobPP
// SIG // Wtbr9c3qzmDJ7J3kUcAm6cltdSHIIFNHESgw6taY1Scy
// SIG // GyBevqIl120XjrIHiPM7tRckHytH1ZGsmvEplR0P7Tn9
// SIG // t5meFvZNEYttkFvad1IEguTlA5LSscXAphi+rVy3zhkl
// SIG // hyCFeGK0yU0+jzbcuURKIxybmRwK5BfVZx0xEVqE4wM3
// SIG // yN5D/uW+GpVHYYAGe7bTrtW1Z13x2qj2Jdqz7NtI4tNy
// SIG // zlVrIf62nYBNe3rOYS/repVdHlR61YbLLETlibs9jFzA
// SIG // re4sO5RTxvS1yho7JqJ59oKLRnRyLhIOSZyTCVZosXeS
// SIG // 0ZZJoGEWSs4cUgsMqBiKtD4WgO2PlT3LeaQh5Io3CCA5
// SIG // tJ5ZCvtCsnqaJXKhptE/xmEETIRyZRjjplUKKd+sFFVG
// SIG // JJVMvvrw1nhIBKOLO4cTepiG39jEiEP4iHzGYCcQuvaL
// SIG // pDFFwqzgt0pBP8SJIKX5dtjDNYrZGd+ZzV5DKJVNZQID
// SIG // AQABo4IBTjCCAUowDgYDVR0PAQH/BAQDAgGGMBAGCSsG
// SIG // AQQBgjcVAQQDAgEAMB0GA1UdDgQWBBR/WT9UIdqtT+8F
// SIG // 5eaj1y0GlBIIMTAZBgkrBgEEAYI3FAIEDB4KAFMAdQBi
// SIG // AEMAQTAPBgNVHRMBAf8EBTADAQH/MB8GA1UdIwQYMBaA
// SIG // FHItOgIxkEO5FAVO4eqnxzHRI4k0MFoGA1UdHwRTMFEw
// SIG // T6BNoEuGSWh0dHA6Ly9jcmwubWljcm9zb2Z0LmNvbS9w
// SIG // a2kvY3JsL3Byb2R1Y3RzL01pY1Jvb0NlckF1dDIwMTFf
// SIG // MjAxMV8wM18yMi5jcmwwXgYIKwYBBQUHAQEEUjBQME4G
// SIG // CCsGAQUFBzAChkJodHRwOi8vd3d3Lm1pY3Jvc29mdC5j
// SIG // b20vcGtpL2NlcnRzL01pY1Jvb0NlckF1dDIwMTFfMjAx
// SIG // MV8wM18yMi5jcnQwDQYJKoZIhvcNAQEMBQADggIBABSU
// SIG // HzgoT+6J5+nyyDCq0pTdVmCsAxYAHXcpjlDtxazPHewf
// SIG // 1v4kOg8V7A5+w+VuMDMGHi8rLXBKn5I8+DVEUYGs8jLu
// SIG // ckc0IeC6owOLUrU3CYdaKRMaO55+T7jwWJ27tPkx0rlR
// SIG // 03tFU0z1YYpcv6Yhaw6N2sUPT+AvjpecnrftoE33pCAk
// SIG // ucUvnGH0iL4J9CZLFQVTGFSOUBbv6oZy4bBBRFMxvH77
// SIG // 9IY4JDvpZKVfbcuhpDeL3Z3e8mukOmkfct+GojNapsWs
// SIG // QYujlJ8jZen5Lrp/3YkxZ2Ay06aTpK/5oOVknwog1TDQ
// SIG // sbY+MDyguTph5tQ0CLfzDaJG2x91BrBT9UG87C6HLkqi
// SIG // wrx9PSKN3wz05rHEfWO+RuKl+0U1/AHQT6NCOjhKI39/
// SIG // c7hWbdKjh5uuWFkBOvXGTNrnhNTAdOXTTYByvYExO8yr
// SIG // yv34PAdqo1vPDE/1heVebr2RramvRUi9kWswKwPqwz7n
// SIG // +iRmM+B6YDGRweEurM1kimAb9FYrAs38YHlPnarl1vW3
// SIG // dGrmJTgefAz3DmCnXN0nveIPsS+KXBIWweeCToAJMGE7
// SIG // v/XS3h9qQ6niWQAAVQ1kUAml3zuS4MisCgi2F6YoK2WA
// SIG // o1EgXK/lXvDxVjIVU0JdL+KvCfwFJkDeVuJ9dNXGNi+A
// SIG // Oxk0BtYd9hxwL30BElj9MYIZ5TCCGeECAQEwbjBXMQsw
// SIG // CQYDVQQGEwJVUzEeMBwGA1UEChMVTWljcm9zb2Z0IENv
// SIG // cnBvcmF0aW9uMSgwJgYDVQQDEx9NaWNyb3NvZnQgQ29k
// SIG // ZSBTaWduaW5nIFBDQSAyMDI0AhMzAAAB/v6KSLXOxGDx
// SIG // AAAAAAH+MA0GCWCGSAFlAwQCAQUAoIGuMBkGCSqGSIb3
// SIG // DQEJAzEMBgorBgEEAYI3AgEEMBwGCisGAQQBgjcCAQsx
// SIG // DjAMBgorBgEEAYI3AgEVMC8GCSqGSIb3DQEJBDEiBCDz
// SIG // w5c1iWCWfLXINeZuaZDhCSqNJU/AtgybDLCksfLILzBC
// SIG // BgorBgEEAYI3AgEMMTQwMqAUgBIATQBpAGMAcgBvAHMA
// SIG // bwBmAHShGoAYaHR0cDovL3d3dy5taWNyb3NvZnQuY29t
// SIG // MA0GCSqGSIb3DQEBAQUABIIBAFEmHlPW8A60JJBs2s1q
// SIG // 3fVlUvpz+b3MoEO7QTf0WKafS4rprQ/8AD2LykEX6sXC
// SIG // uFFNFzoA8KcLsIo0Pi/AEyav7UOobSJOS25xmgfY0uc6
// SIG // 6FrQYY0XZmUf3hRWvDEj0By07OwSkMV9LiSTowm0gqTT
// SIG // PmxDLSUQOwZAua0VIKb4Nqa/dOE6/OTyPjidGDobMW4t
// SIG // n2OCBIYWmXp4ODiRYakYHsMgnsDqwAIm9r6jMBsbJH66
// SIG // uw6PvfUEyRF+//gfEaOk9vKdqKOGLryTPEmHPJUzF3kh
// SIG // JeLWrhxlRqreEFZsXpgqoQYiCpApiIU2MoF4bBdwFBc0
// SIG // IVgCaZ6VX0+J/MqhgheXMIIXkwYKKwYBBAGCNwMDATGC
// SIG // F4Mwghd/BgkqhkiG9w0BBwKgghdwMIIXbAIBAzEPMA0G
// SIG // CWCGSAFlAwQCAQUAMIIBUgYLKoZIhvcNAQkQAQSgggFB
// SIG // BIIBPTCCATkCAQEGCisGAQQBhFkKAwEwMTANBglghkgB
// SIG // ZQMEAgEFAAQggeB539Viea7yfdJwWANDiXepSg+8UVoI
// SIG // 7bxCNGyoRMYCBmoXSuO7mhgTMjAyNjA1MjkwMDQyMzku
// SIG // ODE2WjAEgAIB9KCB0aSBzjCByzELMAkGA1UEBhMCVVMx
// SIG // EzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1Jl
// SIG // ZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3Jh
// SIG // dGlvbjElMCMGA1UECxMcTWljcm9zb2Z0IEFtZXJpY2Eg
// SIG // T3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1Mg
// SIG // RVNOOkE5MzUtMDNFMC1EOTQ3MSUwIwYDVQQDExxNaWNy
// SIG // b3NvZnQgVGltZS1TdGFtcCBTZXJ2aWNloIIR7TCCByAw
// SIG // ggUIoAMCAQICEzMAAAIn1cCDw7EuVy0AAQAAAicwDQYJ
// SIG // KoZIhvcNAQELBQAwfDELMAkGA1UEBhMCVVMxEzARBgNV
// SIG // BAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
// SIG // HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEm
// SIG // MCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENB
// SIG // IDIwMTAwHhcNMjYwMjE5MTk0MDA0WhcNMjcwNTE3MTk0
// SIG // MDA0WjCByzELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldh
// SIG // c2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNV
// SIG // BAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjElMCMGA1UE
// SIG // CxMcTWljcm9zb2Z0IEFtZXJpY2EgT3BlcmF0aW9uczEn
// SIG // MCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOkE5MzUtMDNF
// SIG // MC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1T
// SIG // dGFtcCBTZXJ2aWNlMIICIjANBgkqhkiG9w0BAQEFAAOC
// SIG // Ag8AMIICCgKCAgEA4sVstXwzki+Ko9wNaWncvnpSAy8J
// SIG // xd1Li8ySDlsBh3BIK8ccLZ8r4lCA5pscpU1JdbvtqwT6
// SIG // ds0+AcMEIbxmiaRMarzy5QxZW35kn5SiPOnhaqH4me4/
// SIG // DU0TuJe8BoPTY5vprjWrk3BVtqnXyIyhPedDpK5vTJzD
// SIG // hmMvn4mzWHcUz0T6tU+DC2St7N73TMjBDpXXDkJEiqcQ
// SIG // +v9RpOoDpgrtioCPH9Hser2MZyg5fVtDi0hGv+svNqCG
// SIG // 7JvtUAYnzkOO8VikxtQpr7Rq/OS8wO+fzAHFJkcOf6H/
// SIG // 6hE9FBVdVrpTHCayOgwEgLDQjQfuli66LbgWQI/lTJam
// SIG // 5+UTGekOCGOycGgIiF4e1Y8a58FDmGRvFhBoX6wPfHYv
// SIG // uyxJ/QKr7xDshvlEHI1YQgmzBl4oCV0gKXsnlrqQrA9I
// SIG // 4EDDQsXweQSwQ1sYHWN3SQRD4MX5IEw0CwYILVb9neQm
// SIG // MRyoCCLQeGyOXkm+Y5CBtlqLZxXrU9JXoKcPxKM8H9/W
// SIG // qOrRDWNtXlViM0cPxrJr8I2EBer1a8Tg9KRlbH6hhfLN
// SIG // 1T3mO4SNk8RxTKjQNCAf2tjS2OyU8WACgD/9dRCWbe8W
// SIG // 6gyzIA9WA3RhMxqUIo5t5wDwi9gnmz/45rvdGmydluNu
// SIG // coJRh0yP5wga8EqX0QoMM63xXpSWgijOvt+WhX8CAwEA
// SIG // AaOCAUkwggFFMB0GA1UdDgQWBBTS1ufDeDBkhurne41q
// SIG // oE/dqK30XjAfBgNVHSMEGDAWgBSfpxVdAF5iXYP05dJl
// SIG // pxtTNRnpcjBfBgNVHR8EWDBWMFSgUqBQhk5odHRwOi8v
// SIG // d3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNy
// SIG // b3NvZnQlMjBUaW1lLVN0YW1wJTIwUENBJTIwMjAxMCgx
// SIG // KS5jcmwwbAYIKwYBBQUHAQEEYDBeMFwGCCsGAQUFBzAC
// SIG // hlBodHRwOi8vd3d3Lm1pY3Jvc29mdC5jb20vcGtpb3Bz
// SIG // L2NlcnRzL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQ
// SIG // Q0ElMjAyMDEwKDEpLmNydDAMBgNVHRMBAf8EAjAAMBYG
// SIG // A1UdJQEB/wQMMAoGCCsGAQUFBwMIMA4GA1UdDwEB/wQE
// SIG // AwIHgDANBgkqhkiG9w0BAQsFAAOCAgEAKp3LneD0gtbX
// SIG // m9h+p0bsu7A4iitdxVyYq1QeE38I3aNjG/kC+I+8Gf5O
// SIG // BvT9AgDR2Raw0HCtFRQ08rK2LvGdAIWteGnA2T7MiKD7
// SIG // wBkUYWhxLn+zXJEY5H2v8paNSsiCPI2y/TfbCQKgTy/F
// SIG // eBTQY5Y7/tRhwzsNdu62c+WUkz6AD29kgNL+cg4HKVDH
// SIG // 8YJT8qenJzz6EKU7Q/ThsfA8Jtj/qNUz8QSMuiNE/UWr
// SIG // rpaIFQrysH5X3i03CgL50htawo3q0l5lNQzVzrAA/27K
// SIG // 0o4G1+ZgGw+100TBf72sAFhEhXJ/wY44s8XlmW9NGmEp
// SIG // ZCQNq1bRZTDOPNWlVl3QG1zz+Uc1Ilk5YMh3/xu5QsR2
// SIG // FhiGbgdd092iOmPJhIJ/6LuNGohSaPK9PotD+RnTZ3lr
// SIG // cYkdAjClH5KPubP+93MHtVn6fASl2tu9HInFUGrBX+bE
// SIG // Ve6RZvle3zUV8Aru2p0zpoGu+szu/9rfszpYm76YU/kO
// SIG // mXfgdqmLEp+MQWmPmMx6Z8nC1uXLycoT8QQnG9aEWH4U
// SIG // cwgA29rrSNhLRgo3Nj9oouC8keEDG/5/HDsHi/SKlUyi
// SIG // s81ZPs2ScVd766eC8rkF8NDt9JWugXB3TQAAAfVAvN87
// SIG // NxvXfgJSH2SzPe7TFDSlo2waSIqxcei0wxV1bWUHe4as
// SIG // y2Aco24x9LowggdxMIIFWaADAgECAhMzAAAAFcXna54C
// SIG // m0mZAAAAAAAVMA0GCSqGSIb3DQEBCwUAMIGIMQswCQYD
// SIG // VQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4G
// SIG // A1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0
// SIG // IENvcnBvcmF0aW9uMTIwMAYDVQQDEylNaWNyb3NvZnQg
// SIG // Um9vdCBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkgMjAxMDAe
// SIG // Fw0yMTA5MzAxODIyMjVaFw0zMDA5MzAxODMyMjVaMHwx
// SIG // CzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9u
// SIG // MRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNy
// SIG // b3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jv
// SIG // c29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMIICIjANBgkq
// SIG // hkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA5OGmTOe0ciEL
// SIG // eaLL1yR5vQ7VgtP97pwHB9KpbE51yMo1V/YBf2xK4OK9
// SIG // uT4XYDP/XE/HZveVU3Fa4n5KWv64NmeFRiMMtY0Tz3cy
// SIG // wBAY6GB9alKDRLemjkZrBxTzxXb1hlDcwUTIcVxRMTeg
// SIG // Cjhuje3XD9gmU3w5YQJ6xKr9cmmvHaus9ja+NSZk2pg7
// SIG // uhp7M62AW36MEBydUv626GIl3GoPz130/o5Tz9bshVZN
// SIG // 7928jaTjkY+yOSxRnOlwaQ3KNi1wjjHINSi947SHJMPg
// SIG // yY9+tVSP3PoFVZhtaDuaRr3tpK56KTesy+uDRedGbsoy
// SIG // 1cCGMFxPLOJiss254o2I5JasAUq7vnGpF1tnYN74kpEe
// SIG // HT39IM9zfUGaRnXNxF803RKJ1v2lIH1+/NmeRd+2ci/b
// SIG // fV+AutuqfjbsNkz2K26oElHovwUDo9Fzpk03dJQcNIIP
// SIG // 8BDyt0cY7afomXw/TNuvXsLz1dhzPUNOwTM5TI4CvEJo
// SIG // LhDqhFFG4tG9ahhaYQFzymeiXtcodgLiMxhy16cg8ML6
// SIG // EgrXY28MyTZki1ugpoMhXV8wdJGUlNi5UPkLiWHzNgY1
// SIG // GIRH29wb0f2y1BzFa/ZcUlFdEtsluq9QBXpsxREdcu+N
// SIG // +VLEhReTwDwV2xo3xwgVGD94q0W29R6HXtqPnhZyacau
// SIG // e7e3PmriLq0CAwEAAaOCAd0wggHZMBIGCSsGAQQBgjcV
// SIG // AQQFAgMBAAEwIwYJKwYBBAGCNxUCBBYEFCqnUv5kxJq+
// SIG // gpE8RjUpzxD/LwTuMB0GA1UdDgQWBBSfpxVdAF5iXYP0
// SIG // 5dJlpxtTNRnpcjBcBgNVHSAEVTBTMFEGDCsGAQQBgjdM
// SIG // g30BATBBMD8GCCsGAQUFBwIBFjNodHRwOi8vd3d3Lm1p
// SIG // Y3Jvc29mdC5jb20vcGtpb3BzL0RvY3MvUmVwb3NpdG9y
// SIG // eS5odG0wEwYDVR0lBAwwCgYIKwYBBQUHAwgwGQYJKwYB
// SIG // BAGCNxQCBAweCgBTAHUAYgBDAEEwCwYDVR0PBAQDAgGG
// SIG // MA8GA1UdEwEB/wQFMAMBAf8wHwYDVR0jBBgwFoAU1fZW
// SIG // y4/oolxiaNE9lJBb186aGMQwVgYDVR0fBE8wTTBLoEmg
// SIG // R4ZFaHR0cDovL2NybC5taWNyb3NvZnQuY29tL3BraS9j
// SIG // cmwvcHJvZHVjdHMvTWljUm9vQ2VyQXV0XzIwMTAtMDYt
// SIG // MjMuY3JsMFoGCCsGAQUFBwEBBE4wTDBKBggrBgEFBQcw
// SIG // AoY+aHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraS9j
// SIG // ZXJ0cy9NaWNSb29DZXJBdXRfMjAxMC0wNi0yMy5jcnQw
// SIG // DQYJKoZIhvcNAQELBQADggIBAJ1VffwqreEsH2cBMSRb
// SIG // 4Z5yS/ypb+pcFLY+TkdkeLEGk5c9MTO1OdfCcTY/2mRs
// SIG // fNB1OW27DzHkwo/7bNGhlBgi7ulmZzpTTd2YurYeeNg2
// SIG // LpypglYAA7AFvonoaeC6Ce5732pvvinLbtg/SHUB2Rje
// SIG // bYIM9W0jVOR4U3UkV7ndn/OOPcbzaN9l9qRWqveVtihV
// SIG // J9AkvUCgvxm2EhIRXT0n4ECWOKz3+SmJw7wXsFSFQrP8
// SIG // DJ6LGYnn8AtqgcKBGUIZUnWKNsIdw2FzLixre24/LAl4
// SIG // FOmRsqlb30mjdAy87JGA0j3mSj5mO0+7hvoyGtmW9I/2
// SIG // kQH2zsZ0/fZMcm8Qq3UwxTSwethQ/gpY3UA8x1RtnWN0
// SIG // SCyxTkctwRQEcb9k+SS+c23Kjgm9swFXSVRk2XPXfx5b
// SIG // RAGOWhmRaw2fpCjcZxkoJLo4S5pu+yFUa2pFEUep8beu
// SIG // yOiJXk+d0tBMdrVXVAmxaQFEfnyhYWxz/gq77EFmPWn9
// SIG // y8FBSX5+k77L+DvktxW/tM4+pTFRhLy/AsGConsXHRWJ
// SIG // jXD+57XQKBqJC4822rpM+Zv/Cuk0+CQ1ZyvgDbjmjJnW
// SIG // 4SLq8CdCPSWU5nR0W2rRnj7tfqAxM328y+l7vzhwRNGQ
// SIG // 8cirOoo6CGJ/2XBjU02N7oJtpQUQwXEGahC0HVUzWLOh
// SIG // cGbyoYIDUDCCAjgCAQEwgfmhgdGkgc4wgcsxCzAJBgNV
// SIG // BAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYD
// SIG // VQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3NvZnQg
// SIG // Q29ycG9yYXRpb24xJTAjBgNVBAsTHE1pY3Jvc29mdCBB
// SIG // bWVyaWNhIE9wZXJhdGlvbnMxJzAlBgNVBAsTHm5TaGll
// SIG // bGQgVFNTIEVTTjpBOTM1LTAzRTAtRDk0NzElMCMGA1UE
// SIG // AxMcTWljcm9zb2Z0IFRpbWUtU3RhbXAgU2VydmljZaIj
// SIG // CgEBMAcGBSsOAwIaAxUAIx86rYT8DtBg3JAzAOseeJSI
// SIG // jCqggYMwgYCkfjB8MQswCQYDVQQGEwJVUzETMBEGA1UE
// SIG // CBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEe
// SIG // MBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSYw
// SIG // JAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0Eg
// SIG // MjAxMDANBgkqhkiG9w0BAQsFAAIFAO3DGrEwIhgPMjAy
// SIG // NjA1MjgxOTQ5MDVaGA8yMDI2MDUyOTE5NDkwNVowdzA9
// SIG // BgorBgEEAYRZCgQBMS8wLTAKAgUA7cMasQIBADAKAgEA
// SIG // AgIkfgIB/zAHAgEAAgITjzAKAgUA7cRsMQIBADA2Bgor
// SIG // BgEEAYRZCgQCMSgwJjAMBgorBgEEAYRZCgMCoAowCAIB
// SIG // AAIDB6EgoQowCAIBAAIDAYagMA0GCSqGSIb3DQEBCwUA
// SIG // A4IBAQBXRD9hGCiKRJ0XaurdP9uJg6kwSj+9TPlhYaAj
// SIG // l8GKyy31INEqQk+5/qzcGs0IH6CnXFEV6kLlUIKfTFV3
// SIG // kMobccG2aj7pb8cCwIhkWPi1YGyVPymUUJjk2Is1ZE3S
// SIG // xvtUA2G9+xtMOlV3nyYVB9bJSP1cR+8JiJiV6aFzONKe
// SIG // f9RU0oVhWEgTnEU5+XK1pTa6aT2Y46n6g/u7dV90mYY3
// SIG // l8sZfy5l81uB3imf0Gfwm4OHhEkrIr1yLmbz6JBvUDqc
// SIG // HM+pahV9NY8GrVsTBrTJGD7kUEnrMk2lNS7TlMP4RAyH
// SIG // kGHMoDE77XsI4N/FplKKhRX9jTEFCEQuzCZvcO7cMYIE
// SIG // DTCCBAkCAQEwgZMwfDELMAkGA1UEBhMCVVMxEzARBgNV
// SIG // BAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQx
// SIG // HjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEm
// SIG // MCQGA1UEAxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENB
// SIG // IDIwMTACEzMAAAIn1cCDw7EuVy0AAQAAAicwDQYJYIZI
// SIG // AWUDBAIBBQCgggFKMBoGCSqGSIb3DQEJAzENBgsqhkiG
// SIG // 9w0BCRABBDAvBgkqhkiG9w0BCQQxIgQg6pbDz/9iuju1
// SIG // QlBu8Ru1vre0Udf/7LFYW8dvIRnud1MwgfoGCyqGSIb3
// SIG // DQEJEAIvMYHqMIHnMIHkMIG9BCDl5wEaNaFSHDiySg6p
// SIG // RNGnav42fU13ZZ11kXFxk4QRcjCBmDCBgKR+MHwxCzAJ
// SIG // BgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAw
// SIG // DgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3Nv
// SIG // ZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jvc29m
// SIG // dCBUaW1lLVN0YW1wIFBDQSAyMDEwAhMzAAACJ9XAg8Ox
// SIG // LlctAAEAAAInMCIEIC/RVMIw/ZITyfCJ2OBmu56ErYe8
// SIG // 9JqZJrd7u+vx525zMA0GCSqGSIb3DQEBCwUABIICAKeb
// SIG // Qhr7eblag1fYJi9TpUdnVhcRD1obusnHFNk0mVldd+90
// SIG // K969Ji16RYzk4ti58v+yj13DEqwx4LB1lGIavUKW2c1u
// SIG // SV9CrBSRnGLtTtObrioPWifse37YDBW78PhEcrr2YP39
// SIG // UhvfeXMuw7XmcwA2F0pwAZkNqVun5M55t4OOpTzeEzLd
// SIG // bwsxx+Qf7Wx3ODJo0tV2iaIngKdEMpIUft8KiSz4H3ZG
// SIG // UfOUWxm1EcGX5RRvJjgsEKOt3ObiIPj9UX3mZjGbUb/A
// SIG // +XqUes9BODslV+GnvaSmr/G5DOvD+1ew4uP8eB6L796X
// SIG // F9sHA10Mgj1JRcROFas4hGbTKVTkCI74ZDHrWjQgEm6u
// SIG // QlLv2n9PGIyIa0K1U8eH2Ib+VToaGyblVS3eIOLa77rP
// SIG // YoORXAfDrSYkWm93SJnp2zMIN/ZuT4qRGnjrJM3NlA8R
// SIG // qXgSemOknzMWWyQ4XYkHMgcnGOnLaeiYC3/FlKfQKQ2+
// SIG // dsinY6YvAfvIdhFq1lSBT1Ipoay1nhNZDYM5UrBuuUcH
// SIG // SsvdRuj1QSGQXDmMnV0do/oGUyRJNyIl5WIULSZ2njai
// SIG // wm2BVCxuLEPN6GT/EAPrH80gIDZKDTSC17zHNo8lRG3O
// SIG // B2LkZf1yPhO/mYItWHF3R6mRWinxNrZkUte+qW7DhMsS
// SIG // c9qhZaawESD0EeWLNTY2
// SIG // End signature block
