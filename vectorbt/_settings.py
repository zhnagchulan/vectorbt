"""Global settings.

`settings` config is also accessible via `vectorbt.settings`.

For example, you can change default width and height of each plot:
```python-repl
>>> import vectorbt as vbt

>>> vbt.settings['plotting']['layout']['width'] = 800
>>> vbt.settings['plotting']['layout']['height'] = 400
```

Changes take effect immediately.

!!! note
    All places in vectorbt import `settings` from `vectorbt._settings.settings`, not from `vectorbt`.
    Overwriting `vectorbt.settings` only overwrites the reference created for the user.
    Consider updating the settings config instead of replacing it.

## Saving

Like any other class subclassing `vectorbt.utils.config.Config`, we can save settings to the disk,
load it back, and update in-place:

```python-repl
>>> vbt.settings.save('my_settings')
>>> vbt.settings['caching']['enabled'] = False
>>> vbt.settings['caching']['enabled']
False

>>> vbt.settings.load_update('my_settings')  # load() would return a new object!
>>> vbt.settings['caching']['enabled']
True
```

Bonus: You can do the same with any sub-config inside `settings`!
"""

import numpy as np
import json
import pkgutil
import plotly.io as pio
import plotly.graph_objects as go

from vectorbt.utils.config import Config
from vectorbt.utils.datetime import get_local_tz, get_utc_tz
from vectorbt.utils.decorators import CacheCondition
from vectorbt.utils.template import Sub, RepEval
from vectorbt.base.array_wrapper import ArrayWrapper
from vectorbt.base.column_grouper import ColumnGrouper
from vectorbt.records.col_mapper import ColumnMapper

__pdoc__ = {}


class SettingsConfig(Config):
    """Extends `vectorbt.utils.config.Config` for global settings."""

    def register_template(self, theme: str) -> None:
        """Register template of a theme."""
        pio.templates['vbt_' + theme] = go.layout.Template(self['plotting']['themes'][theme]['template'])

    def register_templates(self) -> None:
        """Register templates of all themes."""
        for theme in self['plotting']['themes']:
            self.register_template(theme)

    def set_theme(self, theme: str) -> None:
        """Set default theme."""
        self.register_template(theme)
        self['plotting']['color_schema'].update(self['plotting']['themes'][theme]['color_schema'])
        self['plotting']['layout']['template'] = 'vbt_' + theme

    def reset_theme(self) -> None:
        """Reset to default theme."""
        self.set_theme('light')


settings = SettingsConfig(
    dict(
        numba=dict(
            check_func_type=True,
            check_func_suffix=False
        ),
        config=Config(),  # flex
        configured=dict(
            config=Config(  # flex
                dict(
                    readonly=True
                )
            ),
        ),
        caching=dict(
            enabled=True,
            whitelist=[
                CacheCondition(base_cls=ArrayWrapper),
                CacheCondition(base_cls=ColumnGrouper),
                CacheCondition(base_cls=ColumnMapper)
            ],
            blacklist=[]
        ),
        broadcasting=dict(
            align_index=False,
            align_columns=True,
            index_from='strict',
            columns_from='stack',
            ignore_sr_names=True,
            drop_duplicates=True,
            keep='last',
            drop_redundant=True,
            ignore_default=True
        ),
        array_wrapper=dict(
            column_only_select=False,
            group_select=True,
            freq=None,
            silence_warnings=False
        ),
        datetime=dict(
            naive_tz=get_local_tz(),
            to_py_timezone=True
        ),
        data=dict(
            tz_localize=get_utc_tz(),
            tz_convert=get_utc_tz(),
            missing_index='nan',
            missing_columns='raise',
            binance=Config(  # flex
                dict(
                    api_key=None,
                    api_secret=None
                )
            ),
            ccxt=Config(  # flex
                dict(
                    enableRateLimit=True
                )
            )
        ),
        plotting=dict(
            use_widgets=True,
            show_kwargs=Config(),  # flex
            color_schema=Config(  # flex
                dict(
                    increasing="#1b9e76",
                    decreasing="#d95f02"
                )
            ),
            contrast_color_schema=Config(  # flex
                dict(
                    blue="#4285F4",
                    orange="#FFAA00",
                    green="#37B13F",
                    red="#EA4335",
                    gray="#E2E2E2"
                )
            ),
            themes=dict(
                light=dict(
                    color_schema=Config(  # flex
                        dict(
                            blue="#1f77b4",
                            orange="#ff7f0e",
                            green="#2ca02c",
                            red="#dc3912",
                            purple="#9467bd",
                            brown="#8c564b",
                            pink="#e377c2",
                            gray="#7f7f7f",
                            yellow="#bcbd22",
                            cyan="#17becf"
                        )
                    ),
                    template=Config(json.loads(pkgutil.get_data(__name__, "templates/light.json"))),  # flex
                ),
                dark=dict(
                    color_schema=Config(  # flex
                        dict(
                            blue="#1f77b4",
                            orange="#ff7f0e",
                            green="#2ca02c",
                            red="#dc3912",
                            purple="#9467bd",
                            brown="#8c564b",
                            pink="#e377c2",
                            gray="#7f7f7f",
                            yellow="#bcbd22",
                            cyan="#17becf"
                        )
                    ),
                    template=Config(json.loads(pkgutil.get_data(__name__, "templates/dark.json"))),  # flex
                ),
                seaborn=dict(
                    color_schema=Config(  # flex
                        dict(
                            blue="rgb(76,114,176)",
                            orange="rgb(221,132,82)",
                            green="rgb(129,114,179)",
                            red="rgb(85,168,104)",
                            purple="rgb(218,139,195)",
                            brown="rgb(204,185,116)",
                            pink="rgb(140,140,140)",
                            gray="rgb(100,181,205)",
                            yellow="rgb(147,120,96)",
                            cyan="rgb(196,78,82)"
                        )
                    ),
                    template=Config(json.loads(pkgutil.get_data(__name__, "templates/seaborn.json"))),  # flex
                ),
            ),
            layout=Config(  # flex
                dict(
                    width=700,
                    height=350,
                    margin=dict(
                        t=30, b=30, l=30, r=30
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        traceorder='normal'
                    )
                )
            ),
        ),
        stats_builder=dict(
            metrics='all',
            tags='all',
            silence_warnings=False,
            template_mapping=Config(),  # flex
            filters=Config(  # flex
                dict(
                    is_not_grouped=dict(
                        filter_func=lambda self, metric_settings:
                        not self.wrapper.grouper.is_grouped(group_by=metric_settings['group_by']),
                        warning_message=Sub("Metric '$metric_name' does not support grouped data")
                    ),
                    has_freq=dict(
                        filter_func=lambda self, metric_settings:
                        self.wrapper.freq is not None,
                        warning_message=Sub("Metric '$metric_name' requires frequency to be set")
                    )
                )
            ),
            settings=Config(  # flex
                dict(
                    to_timedelta=None,
                    use_caching=True
                )
            ),
            metric_settings=Config(),  # flex
        ),
        plot_builder=dict(
            subplots='all',
            tags='all',
            silence_warnings=False,
            template_mapping=Config(),  # flex
            filters=Config(  # flex
                dict(
                    is_not_grouped=dict(
                        filter_func=lambda self, subplot_settings:
                        not self.wrapper.grouper.is_grouped(group_by=subplot_settings['group_by']),
                        warning_message=Sub("Subplot '$subplot_name' does not support grouped data")
                    ),
                    has_freq=dict(
                        filter_func=lambda self, subplot_settings:
                        self.wrapper.freq is not None,
                        warning_message=Sub("Subplot '$subplot_name' requires frequency to be set")
                    )
                )
            ),
            settings=Config(  # flex
                dict(
                    use_caching=True,
                    hline_shape_kwargs=dict(
                        type='line',
                        line=dict(
                            color='gray',
                            dash="dash",
                        )
                    )
                )
            ),
            subplot_settings=Config(),  # flex
            show_titles=True,
            hide_id_labels=True,
            group_id_labels=True,
            make_subplots_kwargs=Config(),  # flex
            kwargs=Config(),  # flex
        ),
        generic=dict(
            stats=Config(  # flex
                dict(
                    filters=dict(
                        has_mapping=dict(
                            filter_func=lambda self, metric_settings:
                            metric_settings.get('mapping', self.mapping) is not None
                        )
                    ),
                    settings=dict(
                        incl_all_keys=False
                    )
                )
            )
        ),
        drawdowns=dict(
            stats=Config(  # flex
                dict(
                    settings=dict(
                        incl_active=False
                    )
                )
            )
        ),
        ohlcv=dict(
            plot_type='OHLC',
            column_names=dict(
                open='Open',
                high='High',
                low='Low',
                close='Close',
                volume='Volume'
            ),
            stats=Config()  # flex
        ),
        signals=dict(
            stats=Config(
                dict(
                    filters=dict(
                        silent_has_other=dict(
                            filter_func=lambda self, metric_settings:
                            metric_settings.get('other', None) is not None
                        ),
                    ),
                    settings=dict(
                        other=None,
                        other_name='Other',
                        from_other=False
                    )
                )
            )  # flex
        ),
        returns=dict(
            year_freq='365 days',
            defaults=Config(  # flex
                dict(
                    start_value=0.,
                    window=10,
                    minp=None,
                    ddof=1,
                    risk_free=0.,
                    levy_alpha=2.,
                    required_return=0.,
                    cutoff=0.05
                )
            ),
            stats=Config(  # flex
                dict(
                    filters=dict(
                        has_year_freq=dict(
                            filter_func=lambda self, metric_settings:
                            self.year_freq is not None,
                            warning_message=Sub("Metric '$metric_name' requires year frequency to be set")
                        ),
                        has_benchmark_rets=dict(
                            filter_func=lambda self, metric_settings:
                            metric_settings.get('benchmark_rets', None) is not None,
                            warning_message=Sub("Metric '$metric_name' requires benchmark_rets to be set")
                        )
                    ),
                    settings=dict(
                        check_is_not_grouped=True
                    )
                )
            )
        ),
        records=dict(
            stats=Config()  # flex
        ),
        mapped_array=dict(
            stats=Config(  # flex
                dict(
                    filters=dict(
                        has_mapping=dict(
                            filter_func=lambda self, metric_settings:
                            metric_settings.get('mapping', self.mapping) is not None
                        )
                    ),
                    settings=dict(
                        incl_all_keys=False
                    )
                )
            )
        ),
        orders=dict(
            stats=Config()  # flex
        ),
        trades=dict(
            stats=Config(  # flex
                dict(
                    filters=dict(
                        is_positions=dict(
                            filter_func=lambda self, metric_settings: self.is_positions
                        )
                    ),
                    settings=dict(
                        incl_open=False
                    ),
                    template_mapping=dict(
                        trades_tag=RepEval("'positions' if self.is_positions else 'trades'"),
                        incl_open_tags=RepEval("['open', 'closed'] if incl_open else ['closed']")
                    )
                )
            )
        ),
        logs=dict(
            stats=Config()  # flex
        ),
        portfolio=dict(
            call_seq='default',
            init_cash=100.,
            size=np.inf,
            size_type='amount',
            fees=0.,
            fixed_fees=0.,
            slippage=0.,
            reject_prob=0.,
            min_size=1e-8,
            max_size=np.inf,
            lock_cash=False,
            allow_partial=True,
            raise_reject=False,
            close_first=False,
            val_price=np.inf,
            accumulate=False,
            sl_stop=np.nan,
            sl_trail=False,
            tp_stop=np.nan,
            stop_entry_price='close',
            stop_exit_price='stoplimit',
            stop_conflict_mode='exit',
            stop_exit_mode='close',
            stop_update_mode='override',
            use_stops=None,
            log=False,
            conflict_mode='ignore',
            signal_direction='longonly',
            order_direction='all',
            cash_sharing=False,
            call_pre_segment=False,
            call_post_segment=False,
            ffill_val_price=True,
            update_value=False,
            fill_pos_record=True,
            row_wise=False,
            use_numba=True,
            seed=None,
            freq=None,
            fillna_close=True,
            stats=Config(  # flex
                dict(
                    filters=dict(
                        has_year_freq=dict(
                            filter_func=lambda self, metric_settings:
                            metric_settings['year_freq'] is not None,
                            warning_message=Sub("Metric '$metric_name' requires year frequency to be set")
                        )
                    ),
                    settings=dict(
                        use_asset_returns=False,
                        use_positions=False,
                        incl_open=False
                    ),
                    template_mapping=dict(
                        trades_tag=RepEval("'positions' if use_positions else 'trades'"),
                        incl_open_tags=RepEval("['open', 'closed'] if incl_open else ['closed']")
                    )
                )
            ),
            plot=Config(  # flex
                dict(
                    subplots=['orders', 'trade_returns', 'cum_returns'],
                    filters=dict(
                        has_year_freq=dict(
                            filter_func=lambda self, subplot_settings:
                            subplot_settings['year_freq'] is not None,
                            warning_message=Sub("Subplot '$subplot_name' requires year frequency to be set")
                        )
                    ),
                    settings=dict(
                        use_asset_returns=False,
                        use_positions=False,
                        incl_open=True
                    ),
                    template_mapping=dict(
                        trades_tag=RepEval("'positions' if use_positions else 'trades'"),
                        incl_open_tags=RepEval("['open', 'closed'] if incl_open else ['closed']")
                    )
                )
            )
        ),
        messaging=dict(
            telegram=Config(  # flex
                dict(
                    token=None,
                    use_context=True,
                    persistence='telegram_bot.pickle',
                    defaults=Config(),  # flex
                    drop_pending_updates=True
                )
            ),
            giphy=dict(
                api_key=None,
                weirdness=5
            ),
        ),
    ),
    copy_kwargs=dict(
        copy_mode='deep'
    ),
    frozen_keys=True,
    nested=True,
    convert_dicts=Config
)
"""_"""

settings.reset_theme()
settings.make_checkpoint()
settings.register_templates()

__pdoc__['settings'] = f"""Global settings config.

## settings.numba

Settings applied to Numba.

```json
{settings['numba'].to_doc()}
```

## settings.config

Settings applied to `vectorbt.utils.config.Config`.

```json
{settings['config'].to_doc()}
```

## settings.configured

Settings applied to `vectorbt.utils.config.Configured`.

```json
{settings['configured'].to_doc()}
```

## settings.caching

Settings applied across `vectorbt.utils.decorators`.

See `vectorbt.utils.decorators.should_cache`.

```json
{settings['caching'].to_doc()}
```

## settings.broadcasting

Settings applied across `vectorbt.base.reshape_fns`.

```json
{settings['broadcasting'].to_doc()}
```

## settings.array_wrapper

Settings applied to `vectorbt.base.array_wrapper.ArrayWrapper`.

```json
{settings['array_wrapper'].to_doc()}
```

## settings.datetime

Settings applied across `vectorbt.utils.datetime`.

```json
{settings['datetime'].to_doc()}
```

## settings.data

Settings applied across `vectorbt.data`.

```json
{settings['data'].to_doc()}
```

### settings.data.binance

See `binance.client.Client`.

### settings.data.ccxt

See [Configuring API Keys](https://ccxt.readthedocs.io/en/latest/manual.html#configuring-api-keys).
Keys can be defined per exchange. If a key is defined at the root, it applies to all exchanges.

## settings.plotting

Settings applied to plotting Plotly figures.

```json
{settings['plotting'].to_doc(replace={
    'settings.plotting.themes.light.template': "{ ... templates/light.json ... }",
    'settings.plotting.themes.dark.template': "{ ... templates/dark.json ... }",
    'settings.plotting.themes.seaborn.template': "{ ... templates/seaborn.json ... }"
}, path='settings.plotting')}
```

## settings.stats_builder

Settings applied to `vectorbt.generic.stats_builder.StatsBuilderMixin`.

```json
{settings['stats_builder'].to_doc()}
```

## settings.plot_builder

Settings applied to `vectorbt.generic.plot_builder.PlotBuilderMixin`.

```json
{settings['plot_builder'].to_doc()}
```

## settings.generic

Settings applied across `vectorbt.generic`.

```json
{settings['generic'].to_doc()}
```

## settings.generic.drawdowns

Settings applied across `vectorbt.generic.drawdowns`.

```json
{settings['drawdowns'].to_doc()}
```

## settings.ohlcv

Settings applied across `vectorbt.ohlcv_accessors`.

```json
{settings['ohlcv'].to_doc()}
```

## settings.signals

Settings applied across `vectorbt.signals`.

```json
{settings['signals'].to_doc()}
```

## settings.returns

Settings applied across `vectorbt.returns`.

```json
{settings['returns'].to_doc()}
```

## settings.records

Settings applied across `vectorbt.records.base`.

```json
{settings['records'].to_doc()}
```

## settings.mapped_array

Settings applied across `vectorbt.records.mapped_array`.

```json
{settings['mapped_array'].to_doc()}
```

## settings.portfolio.orders

Settings applied across `vectorbt.portfolio.orders`.

```json
{settings['orders'].to_doc()}
```

## settings.portfolio.trades

Settings applied across `vectorbt.portfolio.trades`.

```json
{settings['trades'].to_doc()}
```

## settings.portfolio.logs

Settings applied across `vectorbt.portfolio.logs`.

```json
{settings['logs'].to_doc()}
```

## settings.portfolio

Settings applied to `vectorbt.portfolio.base.Portfolio`.

```json
{settings['portfolio'].to_doc()}
```

## settings.messaging

Settings applied across `vectorbt.messaging`.

```json
{settings['messaging'].to_doc()}
```

### settings.messaging.telegram

Settings applied to [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

Set `persistence` to string to use as `filename` in `telegram.ext.PicklePersistence`.
For `defaults`, see `telegram.ext.Defaults`. Other settings will be distributed across 
`telegram.ext.Updater` and `telegram.ext.updater.Updater.start_polling`.

### settings.messaging.giphy

Settings applied to [GIPHY Translate Endpoint](https://developers.giphy.com/docs/api/endpoint#translate).
"""
