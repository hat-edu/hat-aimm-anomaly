import * as plotly from 'plotly.js/dist/plotly.js';
import 'main/index.scss';


export function vt() {
    return plot();
}


export function on_radio_switch(model_type){
    console.log("HELLO " + model_type);

//     r.get('remote', 'timeseries', 'reading')
       hat.conn.send('timeseries', {'model': model_type});
//     let swValue = r.get('remote', 'adapter', String(i) + '+' + '0');
}
export function trigger_notebook(){
        hat.conn.send('timeseries', {'notebook': 1});
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



    return ['div',
        [
            ["label",{props: {for: 'input1'}},' Previous Model '],
            ["input",{props: {disabled: true, id: 'input1',value:  r.get('remote','timeseries','model_before')}}],
            ["label",{props: {for: 'input2'}},' Current Model '],
            ["input",{props: {disabled: true, id: 'input2',value:  r.get('remote','timeseries','model_now')}}]
        ],

        ['div',
            [["input",
            {
                props: {type: 'radio', id: 'id1', name: 'modelSelect', value: 'Forest' },
                on: { click: () => on_radio_switch("Forest") }

            }],
            ["label",{props: {for: 'id1'}},'Forest'],
            ["input",
            {
                props: {type: 'radio', id: 'id2', name: 'modelSelect', value: 'Cluster' },
                on: { click: () => on_radio_switch("Cluster") }

            }],
            ["label",{props: {for: 'id2'}},'Cluster'],
            ["input",
            {
                props: {type: 'radio', id: 'id3', name: 'modelSelect', value: 'constant' },
                on: { click: () => on_radio_switch("constant") }

            }],
            ["label",{props: {for: 'id3'}},'constant']]
        ],
        ["button",
            {
                props: {type: 'checkbox', id: 'id_checkbox', name: 'triggerNotebook', value: 'triggerNotebook' },
                on: { click: () => trigger_notebook() }

            },
            "Run model"
            ],
        ["label",{props: {for: 'id_checkbox'}},''],
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
