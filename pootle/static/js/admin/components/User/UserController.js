/*
 * Copyright (C) Pootle contributors.
 *
 * This file is a part of the Pootle project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import Search from '../Search';

import UserAdd from './UserAdd';
import UserEdit from './UserEdit';


const UserController = React.createClass({

  propTypes: {
    onAdd: React.PropTypes.func.isRequired,
    onCancel: React.PropTypes.func.isRequired,
    onDelete: React.PropTypes.func.isRequired,
    onSearch: React.PropTypes.func.isRequired,
    onSelectItem: React.PropTypes.func.isRequired,
    onSuccess: React.PropTypes.func.isRequired,
    searchQuery: React.PropTypes.string.isRequired,
    selectedItem: React.PropTypes.object,
  },

  render() {
    const viewsMap = {
      add: <UserAdd
              model={this.props.model}
              collection={this.props.items}
              onSuccess={this.props.onSuccess}
              onCancel={this.props.onCancel} />,
      edit: <UserEdit
              model={this.props.selectedItem}
              collection={this.props.items}
              onAdd={this.props.onAdd}
              onSuccess={this.props.onSuccess}
              onDelete={this.props.onDelete} />,
    };
    const args = {
      count: this.props.items.count,
    };

    let msg;
    if (this.props.searchQuery) {
      msg = ngettext('%(count)s user matches your query.',
                     '%(count)s users match your query.', args.count);
    } else {
      msg = ngettext(
        'There is %(count)s user.',
        'There are %(count)s users. Below are the most recently added ones.',
        args.count
      );
    }
    const resultsCaption = interpolate(msg, args, true);

    return (
      <div className="admin-app-users">
        <div className="module first">
          <Search
            fields={['index', 'full_name', 'username', 'email']}
            onSearch={this.props.onSearch}
            onSelectItem={this.props.onSelectItem}
            items={this.props.items}
            selectedItem={this.props.selectedItem}
            searchLabel={gettext('Search Users')}
            searchPlaceholder={gettext('Find user by name, email, properties')}
            resultsCaption={resultsCaption}
            searchQuery={this.props.searchQuery}
          />
        </div>

        <div className="module admin-content">
          {viewsMap[this.props.view]}
        </div>
      </div>
    );
  },

});


export default UserController;
