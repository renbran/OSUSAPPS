/** @odoo-module */

import { registry } from "@web/core/registry"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, onWillUnmount, useEffect } = owl

export class ChartRenderer extends Component {
    setup(){
        this.chartRef = useRef("chart")
        this.actionService = useService("action")
        
        onWillStart(async ()=>{
            // await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js")
            await loadJS("/web/static/lib/Chart/Chart.js")
        })

        useEffect(()=>{
            this.renderChart()            
        }, ()=>[this.props.config])

        onMounted(()=>this.renderChart())
        onWillUnmount(()=>{
            if(this.chart){
                this.chart.destroy();
            }
        })
    }

    renderChart(){
        if(this.chart){
            this.chart.destroy();
        }
        this.chart=new Chart(this.chartRef.el,
        {
          type: this.props.type,
          data: this.props.config.data,
          options: {
              onClick:(e)=>{

                  const [activeElement] = this.chart.getElementAtEvent(e);
                  if (!activeElement){
                      return;
                  }
                  const { _datasetIndex, _index } = activeElement
                  // const active = e.chart.getActiveElements()
                  
                  // if (active.length > 0 && active[0].hasOwnProperty('datasetIndex')){
    
                  let new_domain = this.props.config.domain ? this.props.config.domain : []
                  let label = this.chart.data.datasets[_datasetIndex].labels[_index]
                  // let dataset = this.chart.data.datasets[_datasetIndex].datasetIndex]
                  let data_domain = this.chart.data.datasets[_datasetIndex].domains[_index]
                    
                  // console.log(active)
                  // console.log(e.chart.data.labels)

                  const { label_field, domain} = this.props.config

                  if (data_domain){
                      new_domain = data_domain
                  }                      
                  else if (label_field){
                      new_domain.push([label_field, '=', label])
                  }

                  if (label){
                      if (this.props.title){
                          label = this.props.title + " - " + label
                      }
                  }  
                  else{
                      label = e.chart.data.labels[active[0].index]
                  }

                  // console.log(e.chart.data)
                  
                  this.actionService.doAction({
                      type: "ir.actions.act_window",
                      name: label ? label : this.props.title,
                      res_model: this.props.config.res_model,
                      context:{
                            group_by: ['partner_id'],
                            order_by: ['partner_id asc, date desc']
                        },
                        domain: new_domain,
                        views: [
                            [false, "tree"],
                            [false, "form"]
                        ]
                  })
                              
                  // }
                  
                  
              },
            responsive: true,
            plugins: {
              legend: {
                position: 'bottom',
              },
              title: {
                display: true,
                text: this.props.title,
                position: 'bottom',
              }
            }
          },
        }
      );
    }
}
ChartRenderer.template = "dashboard_custom.ChartRenderer"