import * as plotly from 'plotly.js/dist/plotly.js';
import 'main/index.scss';


export function vt() {
    return plot();
}



export function on_radio_switch(model_type){
    console.log("Picked: " + model_type);
    hat.conn.send('timeseries', {'action': 'model_change', 'model': model_type});
}


export function plot() {
    let l = r.get('remote', 'timeseries','timestamps','reading').length
    const layout = {
        title: 'Timeseries anomaly model testing',
        xaxis: {
            title: 'Timestamp',
            showgrid: true,
            range: [
                // '2013-07-06 06:00:00',
                // '2013-10-06 06:00:00'

                // r.get('remote', 'timeseries','timestamps','reading')[0],
                // r.get('remote', 'timeseries','timestamps','reading')[l-1]
            ]
        },
        yaxis: {
            title: 'Temperature',
            showline: false,
            // range: [0, 2]
        }
    };
    const config = {
        displayModeBar: true,
        responsive: true,
        staticPlot: true
    };

    const reading_trace = {
        x: r.get('remote', 'timeseries','timestamps','reading'),
        y: r.get('remote', 'timeseries','values','reading'),
        line: { shape: 'spline' },
        type: 'scatter',
        name: 'Reading'
    };
    const forecast_trace = {
        x: r.get('remote', 'timeseries','timestamps','forecast'),
        y: r.get('remote', 'timeseries','values','forecast'),
        // line: { shape: 'spline' },
        mode: 'markers',
        type: 'scatter',
        name: 'Forecast'
    };
    const data = [reading_trace, forecast_trace];

    const cur_model_name = r.get('remote','timeseries','info','new_current_model');
    const setting_name = r.get('remote','timeseries','info','setting','name');

    const changed_setting = function (e) {
         console.log("changed to: " + e.target.value);
         hat.conn.send('timeseries', {
             'action': 'setting_change',
             'setting_name': setting_name ,
             'value': e.target.value});
    }

    // function change_model_settings(){
    //    console.log("New setting: " + setting_new_value);
    //    // hat.conn.send('timeseries', {'setting_name': setting , 'value': new_value});
    //
    // }

    return ['div',
        [

            ["label",{props: {for: 'input2'}},' Current Model '],
            ["input",{props: {disabled: true, id: 'input2',value: cur_model_name }}],
            ["br"],
            ["label",{props: {for: 'input1'}}, r.get('remote','timeseries','info','setting','name')  ],
            ["input",{
                props: {
                    disabled: !cur_model_name,
                    id: 'input1',
                    value: r.get('remote','timeseries','info','setting','value')  },
                on: {
                    change: changed_setting

                }
            }],
            ["br"],
            // ["button",
            //         {
            //             props: {disabled: !cur_model_name , type: 'checkbox', id: 'id1', name: 'modelChange', value: 'none' },
            //             on: { click: () => change_model_settings() }
            //
            //         },
            //         "Change model settings"
            // ]

        ],

        ["br"],
        ["br"],
        ['div',
            [
                ["button",
                    {
                        props: {
                            disabled: cur_model_name === 'Forest',
                            type: 'checkbox', id: 'id1',
                            name: 'modelSelect',
                            value: 'Forest' },
                        on: {  click: () => on_radio_switch("Forest") }

                    },
                    "Forest"
                ],
                ["button",
                    {
                        props: {disabled: true , type: 'checkbox', id: 'id2', name: 'modelSelect', value: 'Cluster' },
                        on: { click: () => on_radio_switch("Cluster") }

                    },
                    "Cluster"
                ],
                ["button",
                    {
                        props: {
                            disabled: cur_model_name === 'SVM',
                            type: 'checkbox',
                            id: 'id3',
                            name: 'modelSelect',
                            value: 'SVM' },
                        on: { click: () => on_radio_switch("SVM")}

                    },
                    "SVM"
                ]
            ]
        ],
        ['div.plot', {
            plotData: data,
            props: {
                style: 'height: 100%'
            },
            hook: {
                insert: vnode => plotly.newPlot(vnode.elm, data, layout, config),
                update: (oldVnode, vnode) => {
                    if (u.equals(oldVnode.data.plotData, vnode.data.plotData)) return;
                    plotly.react(vnode.elm, data, layout, config);
                },
                destroy: vnode => plotly.purge(vnode.elm)
            }
        }
        ]

    ];


}
