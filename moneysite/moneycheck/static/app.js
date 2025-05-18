// Vue.component('datepicker', DatePicker);
var currentUrl = window.location.href;
const host = 'http://127.0.0.1:8000';
// Вывод текущего URL в консоль
new Vue({
    el: '#frontend',
    data: {
        cats: [],
        images: ['/static/cat_images/products.png', '/static/cat_images/benzin.png', '/static/cat_images/clothes.png', '/static/cat_images/gift.png', '/static/cat_images/haircut.png', '/static/cat_images/health.png', '/static/cat_images/market.png', '/static/cat_images/restaurant.png', '/static/cat_images/salary.png', '/static/cat_images/sport.png', '/static/cat_images/transport.png'],
        show: false,
        showAddPlan: false,
        showEdPlan: false,
        showAddCat: false,
        showEdCat: false,
        showImageCat: false,
        operation_rus: '',
        formattedDate: '',
        precent: '',
        comment: '',
        cat_image: '',
        sumPlan: '',
        cat_name: '',
        plan_id: '',
        cat_id: '',
        result: '',
        total: '',
        numbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
        operations: ['+', '-', '*', '/'],
        formData: {
            sum: '1',
            comment: '',
            cat_id: '',
            opDate: '',
        },
        formEdPlan: {
            sum: '1',
            plan_id: '',
            cat_id: '',
        },
        formDelPlan: {
            plan_id: '',
        },
        formAddPlan: {
            sum: '1',
            cat_id: '',
        },
        formAddCat: {
            cat_name: '',
            cat_image: '',
            operation: 'profit',
        },
        formEdCat: {
            cat_name: '',
            cat_id: '',
            cat_image: '',
        },
        formDelCat: {
            cat_id: '',
        },
        selectedDate: '',
    },
    created: function () {
        this.selectedDate = this.getCurrentDate();
        const vm = this;
        if (currentUrl == `${host}/spending/`) {
            axios.get('/api/category/spending/')
            .then(function (response){
            vm.cats = response.data.cats;
            vm.total = response.data.total;
            vm.operation = 'spending';
            vm.operation_rus = 'Расходы';

            response.data.cats.forEach(cat => {
                cat.opDate = moment(cat.opDate).tz("Europe/Moscow").format('YYYY-MM-DDTHH:mm:ss');
            });
            var ctx = document.getElementById('pieChart').getContext('2d');

        var pieChart = new Chart(ctx, {
            type: 'pie', // Тип графика - круговая диаграмма
            data: {
                labels: Object.keys(response.data.cats_sum), // Метки для секторов диаграммы
                datasets: [{
                    label: '',
                    data: Object.values(response.data.cats_sum), // Данные для секторов диаграммы
                    backgroundColor: [
                        'rgb(255, 99, 132)', // Цвет первого сектора
                        'rgb(54, 162, 235)', // Цвет второго сектора
                        'rgb(255, 205, 86)',
                        'rgb(255, 87, 51)',
                        'rgb(252, 255, 51)',
                        'rgb(51, 255, 76)',
                        'rgb(51, 214, 255)',
                    ],
                    hoverOffset: 4 // Отступ при наведении на сектор
                }]
            }
        });
            })
        } else {
            axios.get('/api/category/profit/')
            .then(function (response){
            vm.cats = response.data.cats;
            vm.total = response.data.total;
            vm.operation = 'profit';
            vm.operation_rus = 'Доходы';

            response.data.cats.forEach(cat => {
                cat.opDate = moment(cat.opDate).tz("Europe/Moscow").format('YYYY-MM-DDTHH:mm:ss');
            });

            var ctx = document.getElementById('pieChart').getContext('2d');

            var pieChart = new Chart(ctx, {
            type: 'pie', // Тип графика - круговая диаграмма
            data: {
                labels: Object.keys(response.data.cats_sum), // Метки для секторов диаграммы
                datasets: [{
                    label: '',
                    data: Object.values(response.data.cats_sum), // Данные для секторов диаграммы
                    backgroundColor: [
                        'rgb(255, 99, 132)', // Цвет первого сектора
                        'rgb(54, 162, 235)', // Цвет второго сектора
                        'rgb(255, 205, 86)',
                        'rgb(255, 87, 51)',
                        'rgb(252, 255, 51)',
                        'rgb(51, 255, 76)',
                        'rgb(51, 214, 255)',
                    ],
                    hoverOffset: 4 // Отступ при наведении на сектор
                }]
            }
        });
            })
        }
    },
    methods: {
        getCurrentDate() {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hour = String(now.getHours()).padStart(2, '0');
            const minute = String(now.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hour}:${minute}`;
    },
        // handleDateChange(date) {
        //     // Use moment-timezone to adjust to Moscow timezone
        //     const moscowDate = moment(date).tz("Europe/Moscow");
        //     this.selectedDate = moscowDate.format('YYYY-MM-DDTHH:mm:ss.SSS[Z]');
        //     this.formattedDate = moscowDate.format('YYYY-MM-DD');
        //     console.log(this.selectedDate);
        //     },
        openModal: function(name, id, precent, plan_id, plan_sum, image_url) {
            this.show = true;
            this.cat_name = name;
            this.cat_id = id;
            this.precent = precent;
            this.plan_id = plan_id;
            this.sumPlan = plan_sum;
            this.cat_image = image_url;
        },
        openModalAddPlan: function() {
            this.showAddPlan = true;
        },
        openModalEdPlan: function() {
            this.showEdPlan = true;
        },
        openModalAddCat: function() {
            this.showAddCat = true;
        },
        openModalEdCat: function() {
            this.showEdCat = true;
        },
        openModalImageCat: function() {
            this.showImageCat = true;
            console.log(this.images);
        },
        closeModal: function() {
            window.location.reload();
            this.show = false;
        },
        closeModalNoReload: function () {
            this.show = false;
        },
        closeModalEdPlan: function() {
            window.location.reload();
            this.showEdPlan = false;
        },
        closeModalAddPlan: function() {
            this.showAddPlan = false;
        },
        closeModalAddCat: function() {
            this.showAddCat = false;
        },
        closeModalEdCat: function() {
            this.showEdCat = false;
        },
        closeModalImageCat: function() {
            this.showImageCat = false;
        },
        selectImageCat: function(image){
            this.cat_image = image;
            this.showImageCat = false;
            console.log(this.cat_image);
        },
        input: function(num) {
            this.result = this.result.toString();
            this.result += num;
        },
        reset: function() {
            this.result = '';
        },
        calc: function() {
            this.result = eval(this.result);
        },
        del: function() {
            this.result = this.result.slice(0, -1);
        },
        submitForm() {
            const moscowDate = moment(this.selectedDate).tz("Europe/Moscow").format('YYYY-MM-DDTHH:mm:ss.SSS[Z]');
            window.location.reload();
            this.formData.sum = this.result;
            this.formData.comment = this.comment;
            this.formData.cat_id = this.cat_id;
            this.formData.opDate = moscowDate;
            this.result = '';
            axios.post('/api/add-operation/', this.formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
            console.log('Data submitted successfully');
            })
            .catch(error => {
            console.error('Error submitting data:', error);
            });
        },
        submitAddPlan() {
            window.location.reload();
            this.formAddPlan.sum = this.sumPlan;
            this.formAddPlan.cat_id = this.cat_id;
            axios.post('/api/add-plan/', this.formAddPlan, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
            console.log('Data submitted successfully');
            })
            .catch(error => {
            console.error('Error submitting data:', error);
            });
        },
        submitEdPlan() {
//            window.location.reload();
            this.formEdPlan.sum = this.sumPlan;
            this.formEdPlan.plan_id = this.plan_id;
            this.formEdPlan.cat_id = this.cat_id;
            console.log('sumPlan:', this.sumPlan)
            console.log('plan_id:', this.plan_id)
            console.log('cat_id:', this.cat_id)
            axios.post('/api/ed-plan/', this.formEdPlan, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
            console.log('Data submitted successfully');
            })
            .catch(error => {
            console.error('Error submitting data:', error);
            });
        },
        submitDelPlan() {
            window.location.reload();
            this.formDelPlan.plan_id = this.plan_id;
            axios.post('/api/del-plan/', this.formDelPlan, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
            console.log('Data submitted successfully');
            })
            .catch(error => {
            console.error('Error submitting data:', error);
            });
        },
        submitAddCat() {
            if (this.images.includes(this.cat_image)) {

                window.location.reload();
                if (this.operation == 'spending') {
                    this.formAddCat.operation = 'spending';
                }
                this.formAddCat.cat_name = this.cat_name;
                this.formAddCat.cat_image = this.cat_image;
                axios.post('/api/add-cat/', this.formAddCat, {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                })
                .then(response => {
                console.log('Data submitted successfully');
                })
                .catch(error => {
                console.error('Error submitting data:', error);
                });

            } else {
                alert('Выберите картинку')
            }

        },
        submitEdCat() {
            window.location.reload();
            this.formEdCat.cat_name = this.cat_name;
            this.formEdCat.cat_image = this.cat_image;
            this.formEdCat.cat_id = this.cat_id;
            axios.post('/api/ed-cat/', this.formEdCat, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
            console.log('Data submitted successfully');
            })
            .catch(error => {
            console.error('Error submitting data:', error);
            });
        },
        submitDelCat() {
            window.location.reload();
            this.formDelCat.cat_id = this.cat_id;
            axios.post('/api/del-cat/', this.formDelCat, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
            console.log('Data submitted successfully');
            })
            .catch(error => {
            console.error('Error submitting data:', error);
            });
        },
        submitDate() {
        // Здесь можно обработать выбранную дату
            console.log('Выбранная дата:', this.selectedDate);
        },
    }
})