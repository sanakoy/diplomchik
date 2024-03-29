new Vue({
    el: '#frontend',
    data: {
        cats: []
    },
    created: function () {
        const vm = this;
        axios.get('/api/category/')
        .then(function (response){
        vm.cats = response.data
        })

    }
})