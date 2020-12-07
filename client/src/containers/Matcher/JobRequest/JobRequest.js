import React, { Component } from 'react'

import classes from './JobRequest.module.css';
import axios from 'axios';
import Input from '../../../components/Forms/Input/Input';
import Button from '@material-ui/core/Button';
import Modal from '../../../components/UI/Modal/Modal';
import Aux from '../../../hoc/Aux';
import Spinner from '../../../components/UI/Spinner/Spinner';
import Response from '../../../components/Forms/Response/Response';

class JobRequest extends Component {

    state = {
        jobForm: {
            dbName: {
                name:'Database Name',
                elementType: 'input',
                elementConfig: {
                    type: 'text',
                    placeholder: 'Database Name'
                },
                value: '',
                show: true
            },
            tableName: {
                name:'Table Name',
                elementType: 'input',
                elementConfig: {
                    type: 'text',
                    placeholder: 'Table Name'
                },
                value: '',
                show: true
            },
            algorithm: {
                name:'Select algorithm',
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'Coma', displayValue: 'COMA'},
                        {value: 'Cupid', displayValue: 'CUPID'},
                        {value: 'CorrelationClustering', displayValue: 'Distribution Based'},
                        {value: 'JaccardLevenMatcher', displayValue: 'Jaccard Levenshtein'},
                        {value: 'SimilarityFlooding', displayValue: 'Similarity Flooding'}
                        ]
                },
                value: 'Coma',
                show: true
            },
            defaultAlgoParams: {
                name:'Default Algorithm Parameters',
                elementType: 'checkbox',
                elementConfig:{
                    type: 'checkbox',
                    defaultChecked: true,
                    name: 'Default Parameters'
                },
                value: true,
                show: true
            },
            // START OF PARAMS
            // COMA params
            Coma_strategy: {
                name: 'Strategy',
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'COMA_OPT', displayValue: 'Schema'},
                        {value: 'COMA_OPT_INST', displayValue: 'Schema + Instances'}
                        ]
                },
                value: 'COMA_OPT',
                show: false
            },
            Coma_max_n: {
                name: 'max_n',
                elementType: 'range',
                elementConfig : {
                    min: 0,
                    max: 10,
                    step: 1,
                    defaultValue: 0
                },
                value: 0,
                show: false
            },
            // CUPID params
            Cupid_leaf_w_struct: {
                name: 'leaf_w_struct',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.2
                },
                value: 0.2,
                show: false
            },
            Cupid_w_struct: {
                name: 'w_struct',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.2
                },
                value: 0.2,
                show: false
            },
            Cupid_th_accept: {
                name: 'th_accept',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.7
                },
                value: 0.7,
                show: false
            },
            Cupid_th_high: {
                name: 'th_high',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.6
                },
                value: 0.6,
                show: false
            },
            Cupid_th_low: {
                name: 'th_low',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.35
                },
                value: 0.35,
                show: false
            },
            Cupid_th_ns: {
                name: 'th_ns',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.7
                },
                value: 0.7,
                show: false
            },
            // Distribution Based params
            CorrelationClustering_threshold1: {
                name: 'Phase 1 threshold',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.15
                },
                value: 0.15,
                show: false
            },
            CorrelationClustering_threshold2: {
                name: 'Phase 2 threshold',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.15
                },
                value: 0.15,
                show: false
            },
            CorrelationClustering_quantiles: {
                name: 'quantiles',
                elementType: 'range',
                elementConfig : {
                    min: 1,
                    max: 1024,
                    step: 1,
                    defaultValue: 256
                },
                value: 256,
                show: false
            },
            // Jaccard Leven params
            JaccardLevenMatcher_threshold_leven: {
                name: 'th_leven',
                elementType: 'range',
                elementConfig : {
                    min: 0.0,
                    max: 1.0,
                    step: 0.01,
                    defaultValue: 0.8
                },
                value: 0.8,
                show: false
            },
            // END OF PARAMS
            maxNumberOfMatches: {
                name:'Max number of matches',
                elementType: 'input',
                elementConfig: {
                    type: 'number',
                    placeholder: 'Max number of matches'
                },
                value: 1000,
                show: true
            },
            mode: {
                name: 'Schema Matching mode',
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'holistic', displayValue: 'Holistic'},
                        {value: 'internal', displayValue: 'Internal'},
                        {value: 'specifyDB', displayValue: 'Specify Database'}
                        ]
                },
                value: 'holistic',
                show: true
            },
            otherDB: {
                name: 'Other Database Name',
                elementType: 'input',
                elementConfig: {
                    type: 'text',
                    placeholder: 'Database Name'
                },
                value: '',
                show: false
            }
        },
        loading: false,
        responseReceived: false,
        latestResponse: ''
    }


    inputChangedHandler = (event, inputIdentifier) => {
        const updatedJobForm = {
            ...this.state.jobForm
        };
        const updatedJobElement = {
            ...updatedJobForm[inputIdentifier]
        };
        if(inputIdentifier === 'defaultAlgoParams') {
            updatedJobElement.value = !updatedJobElement.value;
            this.toggle_show_dynamic_component(updatedJobForm, updatedJobForm.algorithm.value);
        }else if(inputIdentifier === 'algorithm'){
            if(!updatedJobForm.defaultAlgoParams.value){
                this.toggle_show_dynamic_component(updatedJobForm, updatedJobForm.algorithm.value);
                this.toggle_show_dynamic_component(updatedJobForm, event.target.value);
            }
            updatedJobElement.value = event.target.value;
        }else{
            if (event.target.textContent){
                updatedJobElement.value = parseFloat(event.target.textContent);
            } else {
                 updatedJobElement.value = event.target.value;
                if(inputIdentifier === 'mode' && event.target.value === 'specifyDB'){
                    updatedJobForm['otherDB'].show = true;
                } else if (inputIdentifier === 'mode' && event.target.value !== 'specifyDB'){
                    updatedJobForm['otherDB'].show = false;
                }
            }
        }
        updatedJobForm[inputIdentifier] = updatedJobElement;
        this.setState({jobForm: updatedJobForm});
    }

    toggle_show_dynamic_component = (updatedJobForm, name) => {
        for (let key in updatedJobForm) {
            if (updatedJobForm.hasOwnProperty(key)){
                if (key.startsWith(name)) {
                    updatedJobForm[key].show = !updatedJobForm[key].show;
                }
            }
        }
    }

    jobRequestHandler = ( event ) => {
        event.preventDefault();
        const formData = {};
        for (let formElementId in this.state.jobForm){
            formData[formElementId] = this.state.jobForm[formElementId].value;
        }
        if (formData['dbName'] === ''){
            alert('You must specify the name of the database!');
            return;
        }
        if (formData['tableName'] === ''){
            alert('You must specify the name of the table!');
            return;
        }
        this.setState({loading: true});
        let serverPath = '';
        switch (formData['mode']){
            case 'holistic':
                serverPath = process.env.REACT_APP_SERVER_ADDRESS + '/matches/minio/holistic';
                break;
            case 'internal':
                serverPath = process.env.REACT_APP_SERVER_ADDRESS + '/matches/minio/within_db';
                break;
            case 'specifyDB':
                const otherDB = formData['otherDB'];
                if(otherDB === ''){
                    alert('You must specify the name of the database!');
                    return;
                }
                serverPath = process.env.REACT_APP_SERVER_ADDRESS + '/matches/minio/other_db/' + otherDB;
                break;
            default:
                break;
        }
        const requestBody = {
            "table_name": formData['tableName'],
            "db_name": formData['dbName'],
            "matching_algorithm": formData['algorithm'],
            "max_number_matches": formData['maxNumberOfMatches']
        };
        const algoParams = {}
        if (!formData['defaultAlgoParams']){
            for (let key in formData) {
                if (formData.hasOwnProperty(key)){
                    if (key.startsWith(formData['algorithm'])) {
                        algoParams[key.substr(formData['algorithm'].length + 1)] = formData[key];
                    }
                }
            }
            requestBody['matching_algorithm_params'] = {...algoParams};
        }

        axios({
          method: 'post',
          url: serverPath,
          headers: {},
          data: requestBody})
            .then(response => {this.setState({loading: false, responseReceived: true, latestResponse: response.data});})
            .catch(error => {this.setState( {loading: false} ); console.log(error);})
        // window.location.reload(false);
    }

    closeResponseHandler = () => {
        this.setState({responseReceived: false});
    }

    render () {
        const formElementsArray = [];
        for (let key in this.state.jobForm){
            if (this.state.jobForm[key].show){
                formElementsArray.push({
                    id: key,
                    config: this.state.jobForm[key]
                });
            }
        }
        return (
            <Aux>
                <Modal show={this.state.loading}>
                    <Spinner />
                </Modal>
                <Modal show={this.state.responseReceived} modalClosed={this.closeResponseHandler}>
                    <Response response={this.state.latestResponse}/>
                </Modal>
                <div className={classes.JobRequest}>
                   <h2>Create a Schema matching job</h2>
                    <form onSubmit={this.jobRequestHandler}>
                        {formElementsArray.map(formElement => (
                            <Input
                                key={formElement.id}
                                elementType={formElement.config.elementType}
                                config={formElement.config.elementConfig}
                                name={formElement.config.name}
                                value={formElement.config.value}
                                changed={(event) => this.inputChangedHandler(event, formElement.id)}/>
                                ))
                        }
                        <div className={classes.Button}>
                            <Button variant="contained" color="primary" type="submit">SUBMIT JOB</Button>
                        </div>
                    </form>
               </div>
            </Aux>
        );
    }

}

export default JobRequest;