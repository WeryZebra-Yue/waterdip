import { ReactNode } from 'react';
import { styled } from '@mui/material/styles';
import { Icon } from '@iconify/react';
import { SnackbarProvider } from 'notistack';
import infoFill from '@iconify/icons-eva/info-fill';
import alertCircleFill from '@iconify/icons-eva/alert-circle-fill';
import alertTriangleFill from '@iconify/icons-eva/alert-triangle-fill';
import checkmarkCircle2Fill from '@iconify/icons-eva/checkmark-circle-2-fill';
// material
import { alpha } from '@mui/material/styles';
import { Box } from '@mui/material';
// @types
import { ColorSchema } from '../@types/theme';

const PREFIX = 'NotistackProvider';

const classes = {
  containerRoot: `${PREFIX}-containerRoot`,
  contentRoot: `${PREFIX}-contentRoot`,
  message: `${PREFIX}-message`,
  action: `${PREFIX}-action`,
  variantInfo: `${PREFIX}-variantInfo`,
  variantSuccess: `${PREFIX}-variantSuccess`,
  variantWarning: `${PREFIX}-variantWarning`,
  variantError: `${PREFIX}-variantError`
};



const StyledSnackbarProvider = styled(SnackbarProvider)((
  {
    theme
  }
) => {
  const isLight = theme.palette.mode === 'light';

  const createStyle = {
    color: `black !important`,
    backgroundColor: `white !important`
  };
  return {
    [`& .${classes.containerRoot}`]: {
      backgroundColor: 'white !important',
      color: 'black !important'
    },
    [`& .${classes.contentRoot}`]: {
      width: '100%',
      padding: theme.spacing(1.5),
      margin: theme.spacing(0.25, 0),
      boxShadow: theme.customShadows.z8,
      borderRadius: theme.shape.borderRadius,
      color: theme.palette.grey[isLight ? 0 : 800],
      backgroundColor: theme.palette.grey[isLight ? 900 : 0]
    },
    [`& .${classes.message}`]: {
      padding: 0,
      fontWeight: theme.typography.fontWeightMedium
    },
    [`& .${classes.action}`]: {
      marginRight: -4,
      '& svg': {
        width: 20,
        height: 20,
        opacity: 0.48,
        '&:hover': { opacity: 1 }
      }
    },
    [`&.${classes.variantInfo}`]: { ...createStyle },
    [`&.${classes.variantError}`]: { ...createStyle },
    [`&.${classes.variantSuccess}`]: { ...createStyle },
    [`&.${classes.variantWarning}`]: { ...createStyle },
  };
});

// ----------------------------------------------------------------------

type SnackbarIconProps = {
  icon: Object;
  color: ColorSchema;
};

function SnackbarIcon({ icon, color }: SnackbarIconProps) {
  return (
    <Box
      component="span"
      sx={{
        mr: 1.5,
        width: 40,
        height: 40,
        display: 'flex',
        borderRadius: 1.5,
        alignItems: 'center',
        justifyContent: 'center',
        color: `${color}.main`,
        bgcolor: (theme) => alpha(theme.palette[color].main, 0.16)
      }}
    >
      <Icon icon={icon} width={24} height={24} />
    </Box>
  );
}

type NotistackProviderProps = {
  children: ReactNode;
};

function NotistackProvider({ children }: NotistackProviderProps) {
  

  return (
    <StyledSnackbarProvider
      dense
      maxSnack={5}
      preventDuplicate
      autoHideDuration={3000}
      anchorOrigin={{
        vertical: 'top',
        horizontal: 'right'
      }}
    
      iconVariant={{
        success: <SnackbarIcon icon={checkmarkCircle2Fill} color="success" />,
        error: <SnackbarIcon icon={infoFill} color="error" />,
        warning: <SnackbarIcon icon={alertTriangleFill} color="warning" />,
        info: <SnackbarIcon icon={alertCircleFill} color="info" />
      }}
      classes={classes}
    >
      {children}
    </StyledSnackbarProvider>
  );
}

export default NotistackProvider;
