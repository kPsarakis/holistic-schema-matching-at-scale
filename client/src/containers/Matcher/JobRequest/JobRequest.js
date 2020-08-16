import React, { Component } from 'react'

import classes from './JobRequest.css'
// import axios from '../../../../axios-schema-matching-job'
import Input from '../../../components/Forms/Input/Input'

class JobRequest extends Component {

    state = {
        jobForm: {
            dbName: {
                elementType: 'input',
                elementConfig: {
                    type: 'text',
                    placeholder: 'Database Name'
                },
                value: ''
            },
            tableName: {
                elementType: 'input',
                elementConfig: {
                    type: 'text',
                    placeholder: 'Table Name'
                },
                value: ''
            },
            algorithm: {
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'coma', displayValue: 'COMA'},
                        {value: 'cupid', displayValue: 'CUPID'}
                        ]
                },
                value: ''
            },
            defaultAlgoParams: {
                elementType: 'checkbox',
                elementConfig:{
                    type: 'checkbox',
                    checked: true,
                    name: 'Default Parameters'
                },
                value: ''
            },
            maxNumberOfMatches: {
                elementType: 'input',
                elementConfig: {
                    type: 'number',
                    placeholder: 'Max number of matches'
                },
                value: ''
            },
            mode: {
                elementType: 'select',
                elementConfig: {
                    options: [
                        {value: 'holistic', displayValue: 'Holistic'},
                        {value: 'internal', displayValue: 'Internal'},
                        {value: 'specifyDB', displayValue: 'Specify Database'}
                        ]
                },
                value: ''
            }
        },
        loading: false
    }

    render () {
        const formElementsArray = [];
        for (let key in this.state.jobForm){
            formElementsArray.push({
                id: key,
                config: this.state.jobForm[key]
            })
        }
        return (
           <div className={classes.JobRequest}>
               <h4>Create a Schema matching job</h4>
                <form>
                    {formElementsArray.map(formElement => (
                        <Input
                            key={formElement.id}
                            elementType={formElement.config.elementType}
                            config={formElement.config.elementConfig}
                            value={formElement.config.value} />
                    ))}
                </form>
           </div>
        );
    }

}

export default JobRequest;