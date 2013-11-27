'use strict';
var t;
angular.module('caaRadioServices', ['ngResource']).
factory('LatestSongs', function($http, $resource){
    return $resource('latest.json', {}, {
        get: {
            method: 'GET',
            transformResponse: $http.defaults.transformResponse.concat([function(data, headersGetter) {
                // the json gives us the timestamp in Unix-form, so we convert it to Date objects
                // for easier processing
                var unix_timestamp;
                for(var i=0, l=data['songs'].length; i < l; i++){
                    unix_timestamp = data['songs'][i].timestamp;
                    data['songs'][i].timestamp = new Date(unix_timestamp * 1000);
                }
                return data;
            }])
        }
    });
});
