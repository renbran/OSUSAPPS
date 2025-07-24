/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCard } from "@dashboard_custom/components/kpi_card/kpi_card"
import { ChartRenderer } from "@dashboard_custom/components/chart_renderer/chart_renderer"
// import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, onMounted, useState, hooks } = owl
import { getColor } from "@web/core/colors/colors"

export class DashboardSales extends Component {

    async getMonthlySales(){

        let domain = [
            '&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date', '>=', `${this.state.current_periode.year}-01-01`],
            ['date', '<=', `${this.state.current_periode.year}-12-31`]
        ]

        let prev_domain = [
            '&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date', '>=', `${this.state.previous_periode.year}-01-01`],
            ['date', '<=', `${this.state.previous_periode.year}-12-31`],
        ]

        let res_model = "account.move.line"
    
        // Calculate the sum of invoices for the current periode and last periode
        // const current_revenue = await this.orm.readGroup("account.move.line", domain, ["balance:sum"], [])
        const current_revenue = await this.orm.readGroup(res_model, domain, ['date','balance'],['date:month'], {orderby:'date asc'})
        // const prev_revenue = await this.orm.readGroup("account.move.line", prev_domain, ["balance:sum"], [])
        const prev_revenue = await this.orm.readGroup(res_model, prev_domain, ['date','balance'],['date:month'], {orderby:'date asc'})
        // console.log(current_revenue)
        // const labels = current_revenue.map(d => d['date:month'].split(' ')[0]);

        // Convert the Set back to an array of unique month-year values
        const labels = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",            
        ];

        // console.log(labels.map(l=>current_revenue.filter(q=>l==q['date:month'].split(' ')[0]).map(j=>-j.balance).reduce((a,c)=>a+c,0)))
        
        this.state.monthlySales = {
            
            data:{
              labels: labels,
              datasets: [
                  {
                    label: this.state.current_periode.year,
                    // data: current_revenue.map(d => -d.balance),
                    data: labels.map(l=>current_revenue.filter(q=>l==q['date:month'].split(' ')[0]).map(j=>-j.balance).reduce((a,c)=>a+c,0)),
                    hoverOffset: 4,
                    backgroundColor: getColor(1),
                    domains: current_revenue.map(d => d.__domain),
                    labels: current_revenue.map(d => d['date:month']),
                      
                  },{
                    label: this.state.previous_periode.year,
                    // data: prev_revenue.map(d => -d.balance),
                    data: labels.map(l=>prev_revenue.filter(q=>l==q['date:month'].split(' ')[0]).map(j=>-j.balance).reduce((a,c)=>a+c,0)),
                    hoverOffset: 4,
                    backgroundColor: getColor(2),
                    domains: prev_revenue.map(d => d.__domain),
                    labels: prev_revenue.map(d => d['date:month']),
                  }
              ]
          },
            res_model: res_model,
            domain: domain,
            label_field: 'date:month'
            
        }
    }

    async getTopProduct(){

        let domain = [
            '&','&',
            ['state','in',['sale','done']],
            ['date','>=',this.state.current_periode_start],
            ['date','<=',this.state.current_periode_end]
        ]
        
        const data = await this.orm.readGroup("sale.report",domain,['product_id','price_total'],['product_id'], {limit: 5, orderby:'price_total desc'})
        this.state.topProducts = {            
            data:{
              labels: data.map(d => d.product_id[1]),
              datasets: [
                  {
                      label: 'Total',
                      data: data.map(d => d.price_total),
                      hoverOffset: 4,
                      backgroundColor: data.map((_, index) => getColor(index)),
                  },
                  {
                      label: 'Count',
                      data: data.map(d => d.product_id_count),
                      hoverOffset: 4,
                      backgroundColor: data.map((_, index) => getColor(index)),
                  }
              ]
          }
        }
    }

    async getTopSalesPeople(){
        this.state.topSalesPeople = {
            data:{}
        }
    }

    async getPartnerOrders(){
        this.state.partnerOrders = {
            data:{}
        }
    }
    
    setup(){
        this.state = useState({
            invoiced: {

                all:{

                    thisPeriode:{
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                    lastPeriode: {
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                },
                denmark:{

                    thisPeriode:{
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                    lastPeriode: {
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                },
                eu:{

                    thisPeriode:{
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                    lastPeriode: {
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                },
                foreign:{

                    thisPeriode:{
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                    lastPeriode: {
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                },
                
                
            },

            sale_orders: {

                all: {

                    thisPeriode:{
                        value: 0,
                        percentage: 0,
                        domain: [],
                    },
                    lastPeriode: {
                        value: 0,
                        percentage: 0,
                        domain: [],
                    },
                                        
                },
                web: {

                    thisPeriode:{
                        value: 0,
                        percentage: 0,
                        domain: [],
                    },
                    lastPeriode: {
                        value: 0,
                        percentage: 0,
                        domain: [],
                    },
                                        
                },
                not_web: {

                    thisPeriode:{
                        value: 0,
                        percentage: 0,
                        domain: "",
                    },
                    lastPeriode: {
                        value: 0,
                        percentage: 0,
                        domain: [],
                    },
                                        
                },

                
                open: {
                    value: 0,
                    domain: "",       
                },
                open_lines: {
                    value: 0,
                    domain: "",       
                },
                open_lines_with_error: {
                    value: 0,
                    domain: "",       
                },
                
            },
            
            
            periode: 'month',
            date: new Date(),
            current_periode:{
                year:2023,
            },
            previous_periode:{
                year:2023,
            }
            
        })
        this.orm = useService("orm")
        this.actionService = useService("action")

        onWillStart(async ()=>{
            
            this.getDates();
            await this.getInvoiced();
            await this.getInvoicedDenmark();
            await this.getInvoicedEU();
            await this.getInvoicedForeign();
            await this.getSaleOrders();
            await this.getOpenSaleOrders();
            // await this.getOpenSaleOrderLineWithDifferences();

            await this.getMonthlySales();
            await this.getTopProduct();
            await this.getTopSalesPeople();
            await this.getPartnerOrders();
            
        })

        this.navigateBackward = () => {
            this.changeDate(-1); // You may need to adjust the number based on the selected period
        };

        this.navigateForward = () => {
            this.changeDate(1); // You may need to adjust the number based on the selected period
        };
        
    }

    formatDate(date) {
        return date.toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    }

    getDates(){
        
        // Parse the date string to a JavaScript Date object
        this.state.date = new Date(this.state.date);
        
        if(this.state.periode == 'month'){

            this.state.current_periode_start = new Date(this.state.date.getFullYear(), this.state.date.getMonth(), 1,0,0,0);
            this.state.current_periode_end = new Date(this.state.date.getFullYear(), this.state.date.getMonth()+1, 0,23,59,59);
            
            // this.state.current_date = moment().subtract(this.state.period, 'days').format('L')

            this.state.previous_periode_start = new Date(this.state.date.getFullYear()-1, this.state.date.getMonth(), 1);
            this.state.previous_periode_end = new Date(this.state.date.getFullYear()-1, this.state.date.getMonth()+1, 0);
            
            // this.state.previous_date_start = moment().subtract(this.state.period * 2, 'days').format('L')
        
        }
        else if(this.state.periode == 'day'){

            this.state.current_periode_start = this.state.date;
            this.state.current_periode_end = this.state.date;

            this.state.previous_periode_start = new Date(this.state.date.getFullYear()-1, this.state.date.getMonth(), this.state.date.getDay());
            this.state.previous_periode_end = new Date(this.state.date.getFullYear()-1, this.state.date.getMonth(), this.state.date.getDay());
        
        }
        else if (this.state.periode === 'week') {
            const currentDate = new Date(this.state.date);
        
            // Calculate the current week's start and end dates
            const currentWeekStart = new Date(currentDate);
            currentWeekStart.setDate(currentDate.getDate() - ((currentDate.getDay() + 6) % 7)); // Go back to Monday of the current week
            const currentWeekEnd = new Date(currentWeekStart);
            currentWeekEnd.setDate(currentWeekStart.getDate() + 6);
        
            this.state.current_periode_start = currentWeekStart;
            this.state.current_periode_end = currentWeekEnd;
        
            // Calculate the previous week's start and end dates for the same week in the previous year
            const previousYearDate = new Date(currentDate);
            previousYearDate.setFullYear(previousYearDate.getFullYear() - 1);
        
            const previousWeekStart = new Date(previousYearDate);
            previousWeekStart.setDate(previousYearDate.getDate() - ((previousYearDate.getDay() + 6) % 7)); // Go back to Monday of the same week in the previous year
            const previousWeekEnd = new Date(previousWeekStart);
            previousWeekEnd.setDate(previousWeekStart.getDate() + 6);
        
            this.state.previous_periode_start = previousWeekStart;
            this.state.previous_periode_end = previousWeekEnd;
        }
        else if(this.state.periode == 'quarter'){

            this.state.current_periode_start = new Date(this.state.date.getFullYear(), Math.floor(this.state.date.getMonth() / 3) * 3, 1);
            this.state.current_periode_end = new Date(this.state.date.getFullYear(), Math.floor(this.state.date.getMonth() / 3) * 3 + 3, 0);

            this.state.previous_periode_start = new Date(this.state.date.getFullYear()-1, Math.floor(this.state.date.getMonth() / 3) * 3, 1);
            this.state.previous_periode_end = new Date(this.state.date.getFullYear()-1, Math.floor(this.state.date.getMonth() / 3) * 3 + 3, 0);
        
        }
        else if(this.state.periode == 'halfyear'){

            if (Math.floor(this.state.date.getMonth() / 3) * 3 + 1 <= 6)
            {
                
                this.state.current_periode_start = new Date(this.state.date.getFullYear(), 0, 1);
                this.state.current_periode_end = new Date(this.state.date.getFullYear(), 5, 30);
    
                this.state.previous_periode_start = new Date(this.state.date.getFullYear()-1, 0, 1);
                this.state.previous_periode_end = new Date(this.state.date.getFullYear()-1, 5, 30);

            }
            else{

                this.state.current_periode_start = new Date(this.state.date.getFullYear(), 6, 1);
                this.state.current_periode_end = new Date(this.state.date.getFullYear(), 11, 31);
    
                this.state.previous_periode_start = new Date(this.state.date.getFullYear()-1, 6, 1);
                this.state.previous_periode_end = new Date(this.state.date.getFullYear()-1, 11, 31);
                
            }
            
        }
        else if(this.state.periode == 'year'){

            this.state.current_periode_start = new Date(this.state.date.getFullYear(), 0, 1);
            this.state.current_periode_end = new Date(this.state.date.getFullYear(), 11, 31);

            this.state.previous_periode_start = new Date(this.state.date.getFullYear()-1, 0, 1);
            this.state.previous_periode_end = new Date(this.state.date.getFullYear()-1, 11, 31);
        
        }
        else{

            this.state.current_periode_start = new Date(this.state.date.getFullYear(), 0, 1);
            this.state.current_periode_end = new Date(this.state.date.getFullYear(), 11, 31);

            this.state.previous_periode_start = new Date(this.state.date.getFullYear()-1, 0, 1);
            this.state.previous_periode_end = new Date(this.state.date.getFullYear()-1, 11, 31);
        
        }     

        this.state.current_periode_start_formated = this.formatDate(this.state.current_periode_start);
        this.state.current_periode_end_formated = this.formatDate(this.state.current_periode_end);
        this.state.previous_periode_start_formated = this.formatDate(this.state.previous_periode_start);
        this.state.previous_periode_end_formated = this.formatDate(this.state.previous_periode_end);        
        this.state.date_formated = this.formatDate(this.state.date);

        this.state.current_periode.year = this.state.current_periode_start.getFullYear()
        this.state.previous_periode.year = this.state.previous_periode_start.getFullYear()

        this.state.current_periode_start = `${this.state.current_periode_start.getFullYear()}-${(this.state.current_periode_start.getMonth() + 1).toString().padStart(2, '0')}-${this.state.current_periode_start.getDate().toString().padStart(2, '0')}`;
;
        this.state.current_periode_end = `${this.state.current_periode_end.getFullYear()}-${(this.state.current_periode_end.getMonth() + 1).toString().padStart(2, '0')}-${this.state.current_periode_end.getDate().toString().padStart(2, '0')}`;
        this.state.previous_periode_start = `${this.state.previous_periode_start.getFullYear()}-${(this.state.previous_periode_start.getMonth() + 1).toString().padStart(2, '0')}-${this.state.previous_periode_start.getDate().toString().padStart(2, '0')}`;
        this.state.previous_periode_end = `${this.state.previous_periode_end.getFullYear()}-${(this.state.previous_periode_end.getMonth() + 1).toString().padStart(2, '0')}-${this.state.previous_periode_end.getDate().toString().padStart(2, '0')}`;
        
    }

    async onChangePeriod(){
        
        this.getDates();
        
        console.log("Periode current from " + this.state.current_periode_start + " to " + this.state.current_periode_end);
        console.log("Periode current from " + this.state.previous_periode_start + " to " + this.state.previous_periode_end);
        console.log("Selected Date: " + this.state.date);
        
        await this.getInvoiced();
        await this.getInvoicedDenmark();
        await this.getInvoicedEU();
        await this.getInvoicedForeign();
        await this.getSaleOrders();
        await this.getOpenSaleOrders();
        // await this.getOpenSaleOrderLineWithDifferences();

        await this.getMonthlySales();
        await this.getTopProduct();
        await this.getTopSalesPeople();
        await this.getPartnerOrders();
        
    }    

    async getInvoiced() {

        let domain = [
            '&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date','>=',this.state.current_periode_start],
            ['date','<=',this.state.current_periode_end]
        ]

        let prev_domain = [
            '&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date','>=',this.state.previous_periode_start],
            ['date','<=',this.state.previous_periode_end]
        ]
    
        // Calculate the sum of invoices for the current periode and last periode
        const current_revenue = await this.orm.readGroup("account.move.line", domain, ["balance:sum"], [])
        const prev_revenue = await this.orm.readGroup("account.move.line", prev_domain, ["balance:sum"], [])
        
        // Calculate the percentage increase for this periode
        const percentageIncrease = ((current_revenue[0].balance - prev_revenue[0].balance) / prev_revenue[0].balance) * 100;
    
        // Update the state with the calculated values for this year
        this.state.invoiced.all.thisPeriode.value = (-current_revenue[0].balance / 1000).toFixed(0);
        this.state.invoiced.all.thisPeriode.domain = domain
        this.state.invoiced.all.lastPeriode.value = (-prev_revenue[0].balance / 1000).toFixed(0);
        this.state.invoiced.all.lastPeriode.domain = prev_domain
        this.state.invoiced.all.thisPeriode.percentage = percentageIncrease.toFixed(2);

        
    }

    async getInvoicedDenmark() {

        let domain = [
            '&','&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date','>=',this.state.current_periode_start],
            ['date','<=',this.state.current_periode_end],
            ['partner_id.country_code','=','DK']
            
        ]

        let prev_domain = [
            '&','&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date','>=',this.state.previous_periode_start],
            ['date','<=',this.state.previous_periode_end],
            ['partner_id.country_code','=','DK']
        ]
    
        // Calculate the sum of invoices for the current periode and last periode
        const current_revenue = await this.orm.readGroup("account.move.line", domain, ["balance:sum"], [])
        const prev_revenue = await this.orm.readGroup("account.move.line", prev_domain, ["balance:sum"], [])
        
        // Calculate the percentage increase for this periode
        const percentageIncrease = ((current_revenue[0].balance - prev_revenue[0].balance) / prev_revenue[0].balance) * 100;
    
        // Update the state with the calculated values for this year
        this.state.invoiced.denmark.thisPeriode.value = (-current_revenue[0].balance / 1000).toFixed(0);
        this.state.invoiced.denmark.thisPeriode.domain = domain
        this.state.invoiced.denmark.lastPeriode.value = (-prev_revenue[0].balance / 1000).toFixed(0);
        this.state.invoiced.denmark.lastPeriode.domain = prev_domain
        this.state.invoiced.denmark.thisPeriode.percentage = percentageIncrease.toFixed(2);

        
    }

    async getInvoicedEU() {

        let domain = [
            '&','&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date','>=',this.state.current_periode_start],
            ['date','<=',this.state.current_periode_end],
            ['partner_id.country_id.country_group_ids','in',[1]]
            
        ]

        let prev_domain = [
            '&','&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date','>=',this.state.previous_periode_start],
            ['date','<=',this.state.previous_periode_end],
            ['partner_id.country_id.country_group_ids','in',[1]]
        ]
    
        // Calculate the sum of invoices for the current periode and last periode
        const current_revenue = await this.orm.readGroup("account.move.line", domain, ["balance:sum"], [])
        const prev_revenue = await this.orm.readGroup("account.move.line", prev_domain, ["balance:sum"], [])
        
        // Calculate the percentage increase for this periode
        const percentageIncrease = ((current_revenue[0].balance - prev_revenue[0].balance) / prev_revenue[0].balance) * 100;
    
        // Update the state with the calculated values for this year
        this.state.invoiced.eu.thisPeriode.value = (-current_revenue[0].balance / 1000).toFixed(0);
        this.state.invoiced.eu.thisPeriode.domain = domain
        this.state.invoiced.eu.lastPeriode.value = (-prev_revenue[0].balance / 1000).toFixed(0);
        this.state.invoiced.eu.lastPeriode.domain = prev_domain
        this.state.invoiced.eu.thisPeriode.percentage = percentageIncrease.toFixed(2);

        
    }

    async getInvoicedForeign() {

        let domain = [
            '&','&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date','>=',this.state.current_periode_start],
            ['date','<=',this.state.current_periode_end],
            ['partner_id.country_id.country_group_ids','not in',[1]]
            
        ]

        let prev_domain = [
            '&','&','&','&',
            ['parent_state','=','posted'],
            ['account_id.account_type','=','income'],
            ['date','>=',this.state.previous_periode_start],
            ['date','<=',this.state.previous_periode_end],
            ['partner_id.country_id.country_group_ids','not in',[1]]
        ]
    
        // Calculate the sum of invoices for the current periode and last periode
        const current_revenue = await this.orm.readGroup("account.move.line", domain, ["balance:sum"], [])
        const prev_revenue = await this.orm.readGroup("account.move.line", prev_domain, ["balance:sum"], [])
        
        // Calculate the percentage increase for this periode
        const percentageIncrease = ((current_revenue[0].balance - prev_revenue[0].balance) / prev_revenue[0].balance) * 100;
    
        // Update the state with the calculated values for this year
        this.state.invoiced.foreign.thisPeriode.value = (-current_revenue[0].balance / 1000).toFixed(0);
        this.state.invoiced.foreign.thisPeriode.domain = domain
        this.state.invoiced.foreign.lastPeriode.value = (-prev_revenue[0].balance / 1000).toFixed(0);
        this.state.invoiced.foreign.lastPeriode.domain = prev_domain
        this.state.invoiced.foreign.thisPeriode.percentage = percentageIncrease.toFixed(2);

        
    }

    async getSaleOrders() {

        let domain = [
            '&','&',
            ['state','in',['sale','done']],
            ['date_order','>=',this.state.current_periode_start],
            ['date_order','<=',this.state.current_periode_end]
        ]

        let prev_domain = [
            '&','&',
            ['state','in',['sale','done']],
            ['date_order','>=',this.state.previous_periode_start],
            ['date_order','<=',this.state.previous_periode_end]
        ]
    
        // Calculate the sum of invoices for the current periode and last periode
        const current_sales = await this.orm.readGroup("sale.order", domain, ["amount_untaxed:sum"], [])
        const prev_sales = await this.orm.readGroup("sale.order", prev_domain, ["amount_untaxed:sum"], [])
        
        // Calculate the percentage increase for this periode
        const percentageIncrease = ((current_sales[0].amount_untaxed - prev_sales[0].amount_untaxed) / prev_sales[0].amount_untaxed) * 100;
    
        // Update the state with the calculated values for this year
        this.state.sale_orders.all.thisPeriode.value = (current_sales[0].amount_untaxed / 1000).toFixed(0);
        this.state.sale_orders.all.thisPeriode.domain = domain
        this.state.sale_orders.all.lastPeriode.value = (prev_sales[0].amount_untaxed / 1000).toFixed(0);
        this.state.sale_orders.all.lastPeriode.domain = prev_domain
        this.state.sale_orders.all.thisPeriode.percentage = percentageIncrease.toFixed(2);

        let domain_web = [
            '&','&','&',
            ['state','in',['sale','done']],
            ['date_order','>=',this.state.current_periode_start],
            ['date_order','<=',this.state.current_periode_end],
            ['website_id','!=',false]
        ]

        let prev_domain_web = [
            '&','&','&',
            ['state','in',['sale','done']],
            ['date_order','>=',this.state.previous_periode_start],
            ['date_order','<=',this.state.previous_periode_end],
            ['website_id','!=',false]
        ]
    
        // Calculate the sum of invoices for the current periode and last periode
        const current_sales_web = await this.orm.readGroup("sale.order", domain_web, ["amount_untaxed:sum"], [])
        const prev_sales_web = await this.orm.readGroup("sale.order", prev_domain_web, ["amount_untaxed:sum"], [])
        
        // Calculate the percentage increase for this periode
        const percentageIncrease_web = ((current_sales_web[0].amount_untaxed - prev_sales_web[0].amount_untaxed) / prev_sales_web[0].amount_untaxed) * 100;
    
        // Update the state with the calculated values for this year
        this.state.sale_orders.web.thisPeriode.value = (current_sales_web[0].amount_untaxed / 1000).toFixed(0);
        this.state.sale_orders.web.thisPeriode.domain = domain_web
        this.state.sale_orders.web.lastPeriode.value = (prev_sales_web[0].amount_untaxed / 1000).toFixed(0);
        this.state.sale_orders.web.lastPeriode.domain = prev_domain_web
        this.state.sale_orders.web.thisPeriode.percentage = percentageIncrease_web.toFixed(2);

        let domain_not_web = [
            '&','&','&',
            ['state','in',['sale','done']],
            ['date_order','>=',this.state.current_periode_start],
            ['date_order','<=',this.state.current_periode_end],
            ['website_id','=',false]
        ]

        let prev_domain_not_web = [
            '&','&','&',
            ['state','in',['sale','done']],
            ['date_order','>=',this.state.previous_periode_start],
            ['date_order','<=',this.state.previous_periode_end],
            ['website_id','=',false]
        ]
    
        // Calculate the sum of invoices for the current periode and last periode
        const current_sales_not_web = await this.orm.readGroup("sale.order", domain_not_web, ["amount_untaxed:sum"], [])
        const prev_sales_not_web = await this.orm.readGroup("sale.order", prev_domain_not_web, ["amount_untaxed:sum"], [])
        
        // Calculate the percentage increase for this periode
        const percentageIncrease_not_web = ((current_sales_not_web[0].amount_untaxed - prev_sales_not_web[0].amount_untaxed) / prev_sales_not_web[0].amount_untaxed) * 100;
    
        // Update the state with the calculated values for this year
        this.state.sale_orders.not_web.thisPeriode.value = (current_sales_not_web[0].amount_untaxed / 1000).toFixed(0);
        this.state.sale_orders.not_web.thisPeriode.domain = domain_not_web
        this.state.sale_orders.not_web.lastPeriode.value = (prev_sales_not_web[0].amount_untaxed / 1000).toFixed(0);
        this.state.sale_orders.not_web.lastPeriode.domain = prev_domain_not_web
        this.state.sale_orders.not_web.thisPeriode.percentage = percentageIncrease_not_web.toFixed(2);

        
    }

    async getOpenSaleOrders() {

        let domain = [
            '&',
            ['state','in',['sale','done']],
            ['finished','=',false],
        ]
    
        // Calculate the sum of invoices for the current periode and last periode
        const open_orders = await this.orm.searchCount("sale.order", domain)

        let domain_lines = [
            ['state', 'in', ['sale', 'done']],
            ['product_id.type', '=', 'product'],
            '|', ['qty_to_invoice', '!=', 0], ['qty_to_deliver', '!=', 0],
        ];
        
        const open_orders_value = await this.orm.readGroup("sale.order.line", domain_lines, ["open_salesvalue_base:sum"], [])
                
        // Update the state with the calculated values for this year
        this.state.sale_orders.open.value = open_orders;
        this.state.sale_orders.open.domain = domain;
        this.state.sale_orders.open_lines.value = (open_orders_value[0].open_salesvalue_base / 1000).toFixed(0);
        this.state.sale_orders.open_lines.domain = domain_lines;
        
    }

    // async getOpenSaleOrderLineWithDifferences() {

        // let domain = [
            //    '&',
        //     ['state','in',['sale','done']],           
        //     ['|', ['product_uom_qty', '<', 'qty_delivered'], ['qty_delivered', '!=', 'qty_invoiced']], 

        // ]

        // // Calculate the sum of invoices for the current periode and last periode
        // const open_order_lines = await this.orm.searchCount("sale.order.line", domain)

        // // Update the state with the calculated values for this year
        // this.state.sale_orders.open_lines_with_error.value = open_order_lines;
        // this.state.sale_orders.open_lines_with_error.domain = domain;
        
    // }

    viewInvoicedWithDomain(domain){

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Revenue",
            res_model: "account.move.line",
            context:{
                group_by: ['partner_id'],
                order_by: ['partner_id asc, date desc']
            },
            domain: domain,
            views: [
                [false, "tree"],
                [false, "form"]
            ]
            
        })
        
    }

    viewSaleOrdersWithDomain(domain){

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Sales",
            res_model: "sale.order",
            context:{
                group_by: ['partner_id'],
                order_by: ['partner_id asc, date desc']
            },
            domain: domain,
            views: [
                [false, "tree"],
                [false, "form"]
            ]
            
        })
        
    }

    viewOpenSaleOrders(domain){

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Open Orders",
            res_model: "sale.order",
            context:{
                group_by: ['partner_id'],
                order_by: ['partner_id asc, date desc']
            },
            domain: domain,
            views: [
                [false, "tree"],
                [false, "form"]
            ]
            
        })
        
    }

    viewOpenSaleOrderLines(domain){

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Open Order lines",
            res_model: "sale.order.line",
            context:{
                group_by: ['order_partner_id','order_id'],
                order_by: ['order_partner_id asc, order_id desc']
            },
            domain: domain,
            views: [
                [false, "tree"],
                [false, "form"]
            ]
            
        })
        
    }

    // Add a method to change the date based on the selected period
    changeDate(direction) {
        const currentDate = this.state.date;
        const newDate = new Date(currentDate);

        // Implement logic to adjust the date based on the selected period
        if (this.state.periode === 'day') {
            newDate.setDate(newDate.getDate() + direction);
        } else if (this.state.periode === 'week') {
            newDate.setDate(newDate.getDate() + direction * 7);
        } else if (this.state.periode === 'month') {
            newDate.setMonth(newDate.getMonth() + direction);
        } else if (this.state.periode === 'quarter') {
            newDate.setMonth(newDate.getMonth() + direction * 3);
        } else if (this.state.periode === 'halfyear') {
            newDate.setMonth(newDate.getMonth() + direction * 6);
        } else if (this.state.periode === 'year') {
            newDate.setFullYear(newDate.getFullYear() + direction);
        }

        this.state.date = newDate;
        this.onChangePeriod(); // You can trigger your date change action here
    }


}



DashboardSales.template = "dashboard_sale.DashboardSales"

DashboardSales.components = { KpiCard, ChartRenderer }

registry.category("actions").add("dashboard_sale.DashboardSales", DashboardSales)