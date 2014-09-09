var

    external = function(filename, mid) {
        var list = {
        };
        return (mid in list);
    },

    test = function(filename, mid) {
        var list = {
        };
        return (mid in list) || /^custom\/tests\//.test(mid);
    },

    copyOnly = function(filename, mid) {
        var list = {
            'custom/custom.profile.js': 1,
            'custom/config.js': 1,
            'custom/package.json': 1
        };
        return (mid in list) || /(png|jpg|jpeg|gif|ico)$/.test(filename);
    },

    miniExclude = function(filename, mid) {
        var list = {
        };
        return (mid in list);
    };

var profile = {

    basePath: '../',
    releaseDir: '.',
    releaseName: 'build',

    resourceTags: {
        test: function(filename, mid) {
            return test(filename, mid);
        },
        copyOnly: function(filename, mid) {
            return copyOnly(filename, mid);
        },
        amd: function(filename, mid) {
            return !external(filename, mid) && !test(filename, mid) && !copyOnly(filename, mid) && /\.js$/.test(filename);
        },
        miniExclude: function(filename, mid) {
            return miniExclude(filename, mid);
        }
    }

};
