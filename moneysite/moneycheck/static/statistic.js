// Vue.component('datepicker', DatePicker);
var currentUrl = window.location.href;
const url = new URL(currentUrl);
const host = 'http://127.0.0.1:8000';
// Извлечение отдельных частей URL
const pathnameParts = url.pathname.split('/');
const operation = pathnameParts[2]; // spending
const year = pathnameParts[3]; // 2024
const month = pathnameParts[4]; // 5

console.log('Операция:', operation);
console.log('Год:', year);
console.log('Месяц:', month);

new Vue ({
    el: '#statistic',
//    mounted: function() {
//
//    },
    data: {
        host: 'http://127.0.0.1:8000',
        num: '4345',
        grouped_operation: '',
        operation: '',
        operation_rus: '',
        month: '',
        year: '',
        months_year: '',
        total: '',
        current_month: '',
        current_year: '',
        showEdOp: false,
        opId: '',
        opComment: '',
        showSpending: false,
        showProfit: false,
        opSum: '',
        opKodCat: '',
        catsSum: '',
        numbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
        operations: ['+', '-', '*', '/'],
        formEdOp: {
            opSum: '1',
            opComment: '',
            opId: '',
            opDate: '',
        },
        formDelOp: {
            opId: '',
        },
        selectedDate: new Date(),
        data: {
            labels: ['January', 'February', 'March'],
            datasets: [{ data: [40, 20, 12] }]
        },
        options: {
            responsive: true
        }

    },
    created: function() {
            const vm = this;
        axios.get(`/api/statistic/${operation}/${year}/${month}/`)
        .then(function (response){
            vm.grouped_operation = response.data.grouped_operation;
            vm.operation = response.data.operation;
            vm.month =  response.data.month;
            vm.year =  response.data.year;
            vm.months_year =  response.data.months_year;
            vm.total =  response.data.total;
            vm.current_month = response.data.current_month;
            vm.current_year = response.data.current_year;
            if (response.data.operation == 'spending') {
                this.showSpending = false;
                this.showProfit = true;
                vm.operation_rus = 'Расходы';
            } else {
                this.showSpending = true;
                this.showProfit = false;
                vm.operation_rus = 'Доходы';
            }
            console.log(this.current_year);
            console.log(this.showProfit);


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


    },
    methods: {
        openModalEdOp: function(id, sum, comment){
            this.showEdOp = true;
            this.opId = id;
            this.opSum = sum;
            this.opComment = comment;
        },
        closeModalEdOp: function() {
            this.showEdOp = false;
        },
        input: function(num) {
            this.opSum = this.opSum.toString();
            this.opSum += num;
        },
        reset: function() {
            this.opSum = '';
        },
        calc: function() {
            this.opSum = eval(this.opSum);
        },
        del: function() {
            this.opSum = this.opSum.slice(0, -1);
        },
        submitEdOp() {
            this.formEdOp.opSum = this.opSum;
            this.formEdOp.opComment = this.opComment;
            this.formEdOp.opId = this.opId;
            this.formEdOp.opDate = this.selectedDate;
            this.opSum = '';
            axios.post('/api/ed-operation/', this.formEdOp, {
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
        submitDelOp(id) {
            window.location.reload();
            console.log("id = " + id)
            this.opId = id;
            this.formDelOp.opId = this.opId;
            axios.post('/api/del-operation/', this.formDelOp, {
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

    },
})