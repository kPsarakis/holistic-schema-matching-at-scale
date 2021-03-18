import React, {Component} from "react";
import { CsvToHtmlTable } from 'react-csv-to-table';
import classes from './FabricatedDataPreview.module.css'
// import Aux from '../../../hoc/Aux'

const sampleData = `
Model,mpg,cyl,disp,hp,drat,wt,qsec,vs,am,gear,carb
Mazda RX4,21,6,160,110,3.9,2.62,16.46,0,1,4,4
Mazda RX4 Wag,21,6,160,110,3.9,2.875,17.02,0,1,4,4
Datsun 710,22.8,4,108,93,3.85,2.32,18.61,1,1,4,1
Hornet 4 Drive,21.4,6,258,110,3.08,3.215,19.44,1,0,3,1
Hornet Sportabout,18.7,8,360,175,3.15,3.44,17.02,0,0,3,2
Valiant,18.1,6,225,105,2.76,3.46,20.22,1,0,3,1
Duster 360,14.3,8,360,245,3.21,3.57,15.84,0,0,3,4
Merc 240D,24.4,4,146.7,62,3.69,3.19,20,1,0,4,2
Merc 230,22.8,4,140.8,95,3.92,3.15,22.9,1,0,4,2
Merc 280,19.2,6,167.6,123,3.92,3.44,18.3,1,0,4,4
`;

class  FabricatedDataPreview extends Component {

    render() {
        return(
            <div>
                <div>
                    <h5> Source Table Sample:</h5>
                    <CsvToHtmlTable
                        data={sampleData}
                        csvDelimiter=","
                        tableClassName={classes.Table}
                        tableRowClassName={classes.Row}
                        tableColumnClassName={classes.Column}/>
                        {/*<SampleTable columnNames={this.props.sample['source_column_names']}*/}
                        {/*             sampleData={this.props.sample['source_sample_data']}/>*/}
                    </div>
                    <div>
                        <h5> Target Table Sample:</h5>
                        <CsvToHtmlTable
                            data={sampleData}
                            csvDelimiter=","
                            tableClassName="table table-striped table-hover"/>
                        {/*<SampleTable columnNames={this.props.sample['target_column_names']}*/}
                        {/*             sampleData={this.props.sample['target_sample_data']}/>*/}
                    </div>
            </div>
        );
    }

}

export default FabricatedDataPreview;