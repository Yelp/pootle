/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import assign from 'object-assign';
import React from 'react';

import { FormElement } from 'components/forms';
import { FormMixin } from 'mixins/forms';

import { gotoScreen, verifySocial } from '../actions';
import AuthProgress from './AuthProgress';


const SocialVerification = React.createClass({
  mixins: [FormMixin],

  propTypes: {
    email: React.PropTypes.string.isRequired,
    formErrors: React.PropTypes.object.isRequired,
    isLoading: React.PropTypes.bool.isRequired,
    providerName: React.PropTypes.string.isRequired,
  },


  getInitialState() {
    // XXX: initialData required by `FormMixin`; this is really OBSCURE
    this.initialData = {
      password: '',
    };
    return {
      formData: assign({}, this.initialData),
    };
  },

  componentWillReceiveProps(nextProps) {
    if (this.state.errors !== nextProps.formErrors) {
      this.setState({errors: nextProps.formErrors});
    }
  },


  /* Handlers */

  handleRequestPasswordReset(e) {
    e.preventDefault();
    this.props.dispatch(gotoScreen('requestPasswordReset'));
  },

  handleFormSubmit(e) {
    e.preventDefault();
    this.props.dispatch(verifySocial(this.state.formData));
  },


  /* Others */

  hasData() {
    return this.state.formData.password !== '';
  },


  /* Layout */

  render() {
    if (this.props.redirectTo) {
      return <AuthProgress msg={gettext('Signed in. Redirecting...')} />
    }

    let { errors } = this.state;
    let { formData } = this.state;

    let verificationMsg = interpolate(
      gettext('We found a user with <span>%s</span> email in our system. Please provide the password to finish the sign in procedure. This is a one-off procedure, which will establish a link between your Pootle and %s accounts.'),
      [this.props.email, this.props.providerName]
    );

    return (
      <div className="actions">
        <p dangerouslySetInnerHTML={{__html: verificationMsg}} />
        <div>
          <form
            method="post"
            onSubmit={this.handleFormSubmit}>
            <div className="fields">
              <FormElement
                type="password"
                attribute="password"
                label={gettext('Password')}
                handleChange={this.handleChange}
                formData={formData}
                errors={errors}
              />
              <div className="actions password-forgotten">
                <a href="#" onClick={this.handleRequestPasswordReset}>
                  {gettext('I forgot my password')}
                </a>
              </div>
              {this.renderAllFormErrors()}
            </div>
            <div className="actions">
              <div>
                <input
                  type="submit"
                  className="btn btn-primary"
                  disabled={!this.hasData() | this.props.isLoading}
                  value={gettext('Sign In')}
                />
              </div>
            </div>
          </form>
        </div>
      </div>
    );
  },

});


export default SocialVerification;
